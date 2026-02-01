#!/usr/bin/env python3
"""
Quick test script for CalmRoute API
Run: python test_api.py
"""

import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8000"


def print_full_response(data):
    """Pretty print the full API response"""
    print("\n--- FULL RESPONSE ---")
    print(json.dumps(data, indent=2))
    print("--- END RESPONSE ---\n")


def print_route_summary(route, label="Route"):
    """Print key details from a route"""
    if not route:
        return
    print(f"\n   📍 {label}:")
    print(f"      🕐 Leaving at:  {route.get('suggested_departure_time', 'N/A')}")
    print(f"      🕐 Arriving at: {route.get('expected_arrival_time', 'N/A')}")
    print(f"      ⏱️  Duration:    {route.get('duration_minutes', 'N/A')} mins")
    print(f"      🔄 Changes:     {route.get('number_of_changes', 'N/A')}")
    print(f"      ⭐ Score:       {route.get('overall_score', 'N/A')}")
   
    sensory = route.get('sensory_summary', {})
    print(f"      👥 Crowding:    {sensory.get('crowding', {}).get('level', 'N/A')} - {sensory.get('crowding', {}).get('description', '')}")
    print(f"      🔊 Noise:       {sensory.get('noise', {}).get('level', 'N/A')} - {sensory.get('noise', {}).get('description', '')}")
    print(f"      🌡️  Heat:        {sensory.get('heat', {}).get('level', 'N/A')} - {sensory.get('heat', {}).get('description', '')}")
    print(f"      ✅ Reliability: {sensory.get('reliability', {}).get('level', 'N/A')} - {sensory.get('reliability', {}).get('description', '')}")
   
    if route.get('warnings'):
        print(f"      ⚠️  Warnings:")
        for w in route['warnings']:
            print(f"         - {w}")
   
    if route.get('steps'):
        print(f"      🚶 Steps:")
        for step in route['steps']:
            print(f"         - {step.get('instructions', 'N/A')} ({step.get('duration_minutes', 0)} mins)")


def test_health():
    print("\n" + "=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    r = requests.get(f"{BASE_URL}/health")
    print(f"Status: {r.status_code}")
    print_full_response(r.json())
    return r.status_code == 200


def test_basic_route():
    print("\n" + "=" * 60)
    print("TEST 2: Basic Route (no date/time specified)")
    print("=" * 60)
    print("Request: Kings Cross → Victoria (using current time)")
   
    r = requests.post(f"{BASE_URL}/route", json={
        "origin": "Kings Cross",
        "destination": "Victoria"
    })
    print(f"Status: {r.status_code}")
    data = r.json()
    print_full_response(data)
   
    if data.get("success"):
        print_route_summary(data.get("primary_route"), "Primary Route")
        print_route_summary(data.get("alternative_route"), "Alternative Route")
        return True
    else:
        print(f"❌ Error: {data.get('error')}")
        return False


def test_depart_at_peak():
    print("\n" + "=" * 60)
    print("TEST 3: Depart At - Peak Time (8:30am)")
    print("=" * 60)
   
    # Get next weekday
    tomorrow = date.today() + timedelta(days=1)
    while tomorrow.weekday() >= 5:
        tomorrow += timedelta(days=1)
   
    print(f"Request: Kings Cross → Victoria")
    print(f"         Date: {tomorrow.isoformat()}")
    print(f"         Depart at: 08:30 (PEAK HOURS)")
   
    r = requests.post(f"{BASE_URL}/route", json={
        "origin": "Kings Cross",
        "destination": "Victoria",
        "travel_date": tomorrow.isoformat(),
        "start_time": "08:30",
        "arrive_by": False,
        "preferences": {
            "avoid_crowds": True,
            "avoid_noise": False,
            "avoid_heat": False,
            "prefer_buses": False,
            "minimise_changes": False
        }
    })
    print(f"Status: {r.status_code}")
    data = r.json()
    print_full_response(data)
   
    if data.get("success"):
        print_route_summary(data.get("primary_route"), "Primary Route")
        print_route_summary(data.get("alternative_route"), "Alternative Route")
       
        # Verify peak detection
        desc = data["primary_route"]["sensory_summary"]["crowding"]["description"].lower()
        if "peak" in desc:
            print("\n   ✅ Peak time correctly detected!")
        else:
            print("\n   ⚠️ Peak time NOT mentioned in crowding description")
        return True
    else:
        print(f"❌ Error: {data.get('error')}")
        return False


def test_depart_at_off_peak():
    print("\n" + "=" * 60)
    print("TEST 4: Depart At - Off-Peak Time (11:00am)")
    print("=" * 60)
   
    tomorrow = date.today() + timedelta(days=1)
    while tomorrow.weekday() >= 5:
        tomorrow += timedelta(days=1)
   
    print(f"Request: Kings Cross → Victoria")
    print(f"         Date: {tomorrow.isoformat()}")
    print(f"         Depart at: 11:00 (OFF-PEAK)")
   
    r = requests.post(f"{BASE_URL}/route", json={
        "origin": "Kings Cross",
        "destination": "Victoria",
        "travel_date": tomorrow.isoformat(),
        "start_time": "11:00",
        "arrive_by": False
    })
    print(f"Status: {r.status_code}")
    data = r.json()
    print_full_response(data)
   
    if data.get("success"):
        print_route_summary(data.get("primary_route"), "Primary Route")
        print_route_summary(data.get("alternative_route"), "Alternative Route")
       
        desc = data["primary_route"]["sensory_summary"]["crowding"]["description"].lower()
        if "peak" not in desc:
            print("\n   ✅ Correctly NOT flagged as peak time!")
        else:
            print("\n   ⚠️ Incorrectly flagged as peak time")
        return True
    else:
        print(f"❌ Error: {data.get('error')}")
        return False


def test_arrive_by_peak():
    print("\n" + "=" * 60)
    print("TEST 5: Arrive By - Peak Time (arrive by 9:00am)")
    print("=" * 60)
   
    tomorrow = date.today() + timedelta(days=1)
    while tomorrow.weekday() >= 5:
        tomorrow += timedelta(days=1)
   
    print(f"Request: Paddington → Bank")
    print(f"         Date: {tomorrow.isoformat()}")
    print(f"         Arrive by: 09:00 (PEAK HOURS)")
   
    r = requests.post(f"{BASE_URL}/route", json={
        "origin": "Paddington",
        "destination": "Bank",
        "travel_date": tomorrow.isoformat(),
        "start_time": "09:00",
        "arrive_by": True
    })
    print(f"Status: {r.status_code}")
    data = r.json()
    print_full_response(data)
   
    if data.get("success"):
        print_route_summary(data.get("primary_route"), "Primary Route")
        print_route_summary(data.get("alternative_route"), "Alternative Route")
       
        arrival = data["primary_route"].get("expected_arrival_time", "")
        print(f"\n   Expected arrival: {arrival}")
        print(f"   Requested arrive by: 09:00")
        if arrival and arrival <= "09:00":
            print("   ✅ Arrives on time or early!")
        else:
            print("   ⚠️ May arrive after requested time")
        return True
    else:
        print(f"❌ Error: {data.get('error')}")
        return False


def test_arrive_by_off_peak():
    print("\n" + "=" * 60)
    print("TEST 6: Arrive By - Off-Peak Time (arrive by 14:00)")
    print("=" * 60)
   
    tomorrow = date.today() + timedelta(days=1)
    while tomorrow.weekday() >= 5:
        tomorrow += timedelta(days=1)
   
    print(f"Request: Waterloo → Oxford Circus")
    print(f"         Date: {tomorrow.isoformat()}")
    print(f"         Arrive by: 14:00 (OFF-PEAK)")
   
    r = requests.post(f"{BASE_URL}/route", json={
        "origin": "Waterloo",
        "destination": "Oxford Circus",
        "travel_date": tomorrow.isoformat(),
        "start_time": "14:00",
        "arrive_by": True
    })
    print(f"Status: {r.status_code}")
    data = r.json()
    print_full_response(data)
   
    if data.get("success"):
        print_route_summary(data.get("primary_route"), "Primary Route")
        print_route_summary(data.get("alternative_route"), "Alternative Route")
       
        arrival = data["primary_route"].get("expected_arrival_time", "")
        departure = data["primary_route"].get("suggested_departure_time", "")
        print(f"\n   Will leave at: {departure}")
        print(f"   Will arrive at: {arrival}")
        print(f"   Requested arrive by: 14:00")
        return True
    else:
        print(f"❌ Error: {data.get('error')}")
        return False


def test_evening_peak():
    print("\n" + "=" * 60)
    print("TEST 7: Depart At - Evening Peak (17:30)")
    print("=" * 60)
   
    tomorrow = date.today() + timedelta(days=1)
    while tomorrow.weekday() >= 5:
        tomorrow += timedelta(days=1)
   
    print(f"Request: Liverpool Street → Paddington")
    print(f"         Date: {tomorrow.isoformat()}")
    print(f"         Depart at: 17:30 (EVENING PEAK)")
   
    r = requests.post(f"{BASE_URL}/route", json={
        "origin": "Liverpool Street",
        "destination": "Paddington",
        "travel_date": tomorrow.isoformat(),
        "start_time": "17:30",
        "arrive_by": False,
        "preferences": {
            "avoid_crowds": True,
            "avoid_heat": True,
            "minimise_changes": True
        }
    })
    print(f"Status: {r.status_code}")
    data = r.json()
    print_full_response(data)
   
    if data.get("success"):
        print_route_summary(data.get("primary_route"), "Primary Route")
        print_route_summary(data.get("alternative_route"), "Alternative Route")
       
        desc = data["primary_route"]["sensory_summary"]["crowding"]["description"].lower()
        if "peak" in desc:
            print("\n   ✅ Evening peak correctly detected!")
        else:
            print("\n   ⚠️ Evening peak NOT mentioned")
        return True
    else:
        print(f"❌ Error: {data.get('error')}")
        return False


def test_weekend():
    print("\n" + "=" * 60)
    print("TEST 8: Weekend Travel (should NOT be peak)")
    print("=" * 60)
   
    # Find next Saturday
    next_saturday = date.today()
    while next_saturday.weekday() != 5:
        next_saturday += timedelta(days=1)
   
    print(f"Request: Kings Cross → Victoria")
    print(f"         Date: {next_saturday.isoformat()} (Saturday)")
    print(f"         Depart at: 08:30 (would be peak on weekday)")
   
    r = requests.post(f"{BASE_URL}/route", json={
        "origin": "Kings Cross",
        "destination": "Victoria",
        "travel_date": next_saturday.isoformat(),
        "start_time": "08:30",
        "arrive_by": False
    })
    print(f"Status: {r.status_code}")
    data = r.json()
    print_full_response(data)
   
    if data.get("success"):
        print_route_summary(data.get("primary_route"), "Primary Route")
       
        desc = data["primary_route"]["sensory_summary"]["crowding"]["description"].lower()
        if "peak" not in desc:
            print("\n   ✅ Weekend correctly NOT flagged as peak!")
        else:
            print("\n   ⚠️ Weekend incorrectly flagged as peak")
        return True
    else:
        print(f"❌ Error: {data.get('error')}")
        return False


def test_postcode_to_postcode():
    print("\n" + "=" * 60)
    print("TEST 9: Postcode to Postcode")
    print("=" * 60)
   
    tomorrow = date.today() + timedelta(days=1)
   
    print(f"Request: SW1A 1AA (Buckingham Palace) → E1 6AN (Whitechapel)")
    print(f"         Date: {tomorrow.isoformat()}")
    print(f"         Depart at: 10:00")
   
    r = requests.post(f"{BASE_URL}/route", json={
        "origin": "SW1A 1AA",
        "destination": "E1 6AN",
        "travel_date": tomorrow.isoformat(),
        "start_time": "10:00",
        "arrive_by": False
    })
    print(f"Status: {r.status_code}")
    data = r.json()
    print_full_response(data)
   
    if data.get("success"):
        print_route_summary(data.get("primary_route"), "Primary Route")
        print("\n   ✅ Postcode routing works!")
        return True
    else:
        print(f"❌ Error: {data.get('error')}")
        return False


def test_address_to_station():
    print("\n" + "=" * 60)
    print("TEST 10: Address to Station")
    print("=" * 60)
   
    tomorrow = date.today() + timedelta(days=1)
   
    print(f"Request: 10 Downing Street → Kings Cross")
    print(f"         Date: {tomorrow.isoformat()}")
    print(f"         Depart at: 09:30")
   
    r = requests.post(f"{BASE_URL}/route", json={
        "origin": "10 Downing Street, London",
        "destination": "Kings Cross",
        "travel_date": tomorrow.isoformat(),
        "start_time": "09:30",
        "arrive_by": False
    })
    print(f"Status: {r.status_code}")
    data = r.json()
    print_full_response(data)
   
    if data.get("success"):
        print_route_summary(data.get("primary_route"), "Primary Route")
        print("\n   ✅ Address to station routing works!")
        return True
    else:
        print(f"❌ Error: {data.get('error')}")
        return False


def test_address_to_address():
    print("\n" + "=" * 60)
    print("TEST 11: Address to Address")
    print("=" * 60)
   
    tomorrow = date.today() + timedelta(days=1)
   
    print(f"Request: British Museum → Tower of London")
    print(f"         Date: {tomorrow.isoformat()}")
    print(f"         Arrive by: 11:00")
   
    r = requests.post(f"{BASE_URL}/route", json={
        "origin": "British Museum, London",
        "destination": "Tower of London",
        "travel_date": tomorrow.isoformat(),
        "start_time": "11:00",
        "arrive_by": True
    })
    print(f"Status: {r.status_code}")
    data = r.json()
    print_full_response(data)
   
    if data.get("success"):
        print_route_summary(data.get("primary_route"), "Primary Route")
        arrival = data["primary_route"].get("expected_arrival_time", "")
        departure = data["primary_route"].get("suggested_departure_time", "")
        print(f"\n   Leave at {departure} to arrive by {arrival}")
        print("   ✅ Address to address routing works!")
        return True
    else:
        print(f"❌ Error: {data.get('error')}")
        return False


if __name__ == "__main__":
    print("\n" + "🚇" * 30)
    print("   CalmRoute TfL API - Full Test Suite")
    print("🚇" * 30)
   
    results = []
   
    try:
        results.append(("1. Health Check", test_health()))
        results.append(("2. Basic Route (no time)", test_basic_route()))
        results.append(("3. Depart At - Peak (8:30am)", test_depart_at_peak()))
        results.append(("4. Depart At - Off-Peak (11:00am)", test_depart_at_off_peak()))
        results.append(("5. Arrive By - Peak (9:00am)", test_arrive_by_peak()))
        results.append(("6. Arrive By - Off-Peak (14:00)", test_arrive_by_off_peak()))
        results.append(("7. Evening Peak (17:30)", test_evening_peak()))
        results.append(("8. Weekend (not peak)", test_weekend()))
        results.append(("9. Postcode to Postcode", test_postcode_to_postcode()))
        results.append(("10. Address to Station", test_address_to_station()))
        results.append(("11. Address to Address", test_address_to_address()))
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server!")
        print("   Make sure the server is running:")
        print("   uvicorn main:app --reload --port 8000")
        exit(1)
   
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = 0
    failed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        if result:
            passed += 1
        else:
            failed += 1
        print(f"{status}: {name}")
   
    print(f"\nTotal: {passed}/{len(results)} passed")