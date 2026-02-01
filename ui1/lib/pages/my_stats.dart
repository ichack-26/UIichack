import 'dart:convert';
import 'dart:math';

import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:ui1/models/journey.dart';

class MyStatsPage extends StatefulWidget {
  const MyStatsPage({super.key});

  @override
  State<MyStatsPage> createState() => _MyStatsPageState();
}

class _MyStatsPageState extends State<MyStatsPage> {
  List<Journey> _journeys = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadJourneys();
  }

  Future<void> _loadJourneys() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final journeysJson = prefs.getStringList('journeys') ?? [];
      final journeys = <Journey>[];

      for (final jsonStr in journeysJson) {
        try {
          final data = jsonDecode(jsonStr) as Map<String, dynamic>;
          if (data.containsKey('fromLat') &&
              data.containsKey('fromLng') &&
              data.containsKey('toLat') &&
              data.containsKey('toLng')) {
            journeys.add(Journey.fromJson(data));
          }
        } catch (_) {
          // Ignore malformed journeys
        }
      }

      if (!mounted) return;
      setState(() {
        _journeys = journeys;
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _loading = false;
      });
    }
  }

  double _calculateDistanceKm(List<Map<String, double>> points) {
    if (points.length < 2) return 0;
    double total = 0;
    for (int i = 0; i < points.length - 1; i++) {
      final p1 = points[i];
      final p2 = points[i + 1];
      final lat1 = (p1['lat'] ?? 0) * pi / 180;
      final lat2 = (p2['lat'] ?? 0) * pi / 180;
      final dLat = lat2 - lat1;
      final dLon = ((p2['lng'] ?? 0) - (p1['lng'] ?? 0)) * pi / 180;
      final a = sin(dLat / 2) * sin(dLat / 2) +
          cos(lat1) * cos(lat2) * sin(dLon / 2) * sin(dLon / 2);
      final c = 2 * asin(sqrt(a));
      total += 6371 * c;
    }
    return total;
  }

  Map<DateTime, double> _distanceByMonth() {
    final Map<DateTime, double> totals = {};
    for (final journey in _journeys) {
      final date = DateTime(journey.date.year, journey.date.month);
      final distanceKm = _calculateDistanceKm(journey.polylinePoints);
      totals[date] = (totals[date] ?? 0) + distanceKm;
    }
    return totals;
  }

  Map<String, double> _distanceByMode() {
    final Map<String, double> totals = {};

    for (final journey in _journeys) {
      final totalDistance = _calculateDistanceKm(journey.polylinePoints);
      final steps = journey.steps ?? [];

      if (steps.isEmpty) {
        totals['unknown'] = (totals['unknown'] ?? 0) + totalDistance;
        continue;
      }

      final totalStepDuration = steps.fold<int>(
        0,
        (sum, s) => sum + (s.durationMinutes > 0 ? s.durationMinutes : 1),
      );

      for (final step in steps) {
        final duration = step.durationMinutes > 0 ? step.durationMinutes : 1;
        final share = totalStepDuration == 0 ? 0 : duration / totalStepDuration;
        final distanceShare = totalDistance * share;
        final key = step.mode.trim().isEmpty ? 'unknown' : step.mode.toLowerCase();
        totals[key] = (totals[key] ?? 0) + distanceShare;
      }
    }

    return totals;
  }

  List<DateTime> _lastSixMonths() {
    final now = DateTime.now();
    final months = <DateTime>[];
    for (int i = 5; i >= 0; i--) {
      months.add(DateTime(now.year, now.month - i));
    }
    return months;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        title: const Text('My Stats'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadJourneys,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(20),
              children: [
                _buildSummaryCards(theme),
                const SizedBox(height: 20),
                _buildMonthlyDistanceChart(theme),
                const SizedBox(height: 20),
                _buildModeBreakdownChart(theme),
              ],
            ),
    );
  }

  Widget _buildSummaryCards(ThemeData theme) {
    final totalDistance = _journeys.fold<double>(
      0,
      (sum, j) => sum + _calculateDistanceKm(j.polylinePoints),
    );

    final totalTrips = _journeys.length;
    final totalMinutes = _journeys.fold<int>(
      0,
      (sum, j) => sum + (j.durationMinutes ?? 0),
    );

    return Row(
      children: [
        Expanded(
          child: _StatCard(
            title: 'Distance',
            value: '${totalDistance.toStringAsFixed(1)} km',
            icon: Icons.route,
            color: Colors.blue,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _StatCard(
            title: 'Trips',
            value: '$totalTrips',
            icon: Icons.directions_walk,
            color: Colors.green,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _StatCard(
            title: 'Time',
            value: '${(totalMinutes / 60).toStringAsFixed(1)} h',
            icon: Icons.access_time,
            color: Colors.orange,
          ),
        ),
      ],
    );
  }

  Widget _buildMonthlyDistanceChart(ThemeData theme) {
    final monthlyTotals = _distanceByMonth();
    final months = _lastSixMonths();
    final formatter = DateFormat('MMM');

    final spots = <BarChartGroupData>[];
    for (int i = 0; i < months.length; i++) {
      final m = months[i];
      final distance = monthlyTotals[m] ?? 0;
      spots.add(
        BarChartGroupData(
          x: i,
          barRods: [
            BarChartRodData(
              toY: distance,
              width: 18,
              color: Colors.blue,
              borderRadius: BorderRadius.circular(6),
            ),
          ],
        ),
      );
    }

    return _SectionCard(
      title: 'Distance by Month',
      child: SizedBox(
        height: 240,
        child: BarChart(
          BarChartData(
            barGroups: spots,
            borderData: FlBorderData(show: false),
            gridData: FlGridData(show: true, drawVerticalLine: false),
            titlesData: FlTitlesData(
              leftTitles: AxisTitles(
                sideTitles: SideTitles(showTitles: true, reservedSize: 40),
              ),
              rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
              topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
              bottomTitles: AxisTitles(
                sideTitles: SideTitles(
                  showTitles: true,
                  getTitlesWidget: (value, meta) {
                    final index = value.toInt();
                    if (index < 0 || index >= months.length) {
                      return const SizedBox.shrink();
                    }
                    return Padding(
                      padding: const EdgeInsets.only(top: 8.0),
                      child: Text(formatter.format(months[index])),
                    );
                  },
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildModeBreakdownChart(ThemeData theme) {
    final modeTotals = _distanceByMode();

    if (modeTotals.isEmpty) {
      return _SectionCard(
        title: 'Distance by Mode',
        child: const Padding(
          padding: EdgeInsets.all(16.0),
          child: Text('No journeys yet. Plan a route to see stats.'),
        ),
      );
    }

    final total = modeTotals.values.fold<double>(0, (sum, v) => sum + v);
    final colors = [
      Colors.blue,
      Colors.green,
      Colors.orange,
      Colors.purple,
      Colors.red,
      Colors.teal,
      Colors.grey,
    ];

    final entries = modeTotals.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    final sections = <PieChartSectionData>[];
    for (int i = 0; i < entries.length; i++) {
      final entry = entries[i];
      final value = entry.value;
      final percent = total == 0 ? 0 : (value / total) * 100;
      sections.add(
        PieChartSectionData(
          color: colors[i % colors.length],
          value: value,
          title: '${percent.toStringAsFixed(0)}%',
          radius: 50,
          titleStyle: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      );
    }

    return _SectionCard(
      title: 'Distance by Mode',
      child: Column(
        children: [
          SizedBox(
            height: 220,
            child: PieChart(
              PieChartData(
                sections: sections,
                centerSpaceRadius: 40,
                sectionsSpace: 2,
              ),
            ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 12,
            runSpacing: 8,
            children: [
              for (int i = 0; i < entries.length; i++)
                _LegendChip(
                  label: '${entries[i].key} (${entries[i].value.toStringAsFixed(1)} km)',
                  color: colors[i % colors.length],
                ),
            ],
          ),
        ],
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({required this.title, required this.child});

  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            child,
          ],
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  const _StatCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
  });

  final String title;
  final String value;
  final IconData icon;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: color.withOpacity(0.08),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: const TextStyle(fontSize: 12, color: Colors.black54),
          ),
        ],
      ),
    );
  }
}

class _LegendChip extends StatelessWidget {
  const _LegendChip({required this.label, required this.color});

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 6),
        Text(label, style: const TextStyle(fontSize: 12)),
      ],
    );
  }
}
