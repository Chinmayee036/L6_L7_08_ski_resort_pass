import pytest

from ski_resort_pass import (
    process_resort_bookings,
    check_chairlift_anemometer
)


# ==========================================
# TESTS FOR process_resort_bookings()
# ==========================================

def test_invalid_groups():
    with pytest.raises(ValueError):
        process_resort_bookings("invalid", 15.0)


def test_negative_facility_fee():
    with pytest.raises(ValueError):
        process_resort_bookings([], -5.0)


def test_empty_groups():
    result = process_resort_bookings([], 15.0)
    assert result["status"] == "ZERO_SALES"


def test_inactive_group():
    result = process_resort_bookings(
        [{"is_active": False}], 15.0
    )
    assert result["status"] == "ZERO_SALES"


def test_season_pass():
    groups = [{
        "is_active": True,
        "duration": "season",
        "skiers": [{"age": 30}]
    }]
    result = process_resort_bookings(groups, 15.0)
    assert result["total_revenue"] == 300.0


def test_full_day_pass():
    groups = [{
        "is_active": True,
        "duration": "full_day",
        "skiers": [{"age": 30}]
    }]
    result = process_resort_bookings(groups, 15.0)
    assert result["total_revenue"] == 80.0


def test_half_day_pass():
    groups = [{
        "is_active": True,
        "duration": "half_day",
        "skiers": [{"age": 30}]
    }]
    result = process_resort_bookings(groups, 15.0)
    assert result["total_revenue"] == 50.0


def test_invalid_duration():
    groups = [{
        "is_active": True,
        "duration": "weekly",
        "skiers": [{"age": 30}]
    }]
    result = process_resort_bookings(groups, 15.0)
    assert result["status"] == "ZERO_SALES"


def test_empty_skiers():
    groups = [{
        "is_active": True,
        "duration": "full_day",
        "skiers": []
    }]
    result = process_resort_bookings(groups, 15.0)
    assert result["status"] == "ZERO_SALES"


def test_invalid_age_zero():
    groups = [{
        "is_active": True,
        "duration": "full_day",
        "skiers": [{"age": 0}]
    }]
    result = process_resort_bookings(groups, 15.0)
    assert result["status"] == "ZERO_SALES"


def test_invalid_age_negative():
    groups = [{
        "is_active": True,
        "duration": "full_day",
        "skiers": [{"age": -5}]
    }]
    result = process_resort_bookings(groups, 15.0)
    assert result["status"] == "ZERO_SALES"


def test_child_discount():
    groups = [{
        "is_active": True,
        "duration": "full_day",
        "skiers": [{"age": 10}]
    }]
    result = process_resort_bookings(groups, 15.0)
    assert result["total_revenue"] == 48.0


def test_senior_discount():
    groups = [{
        "is_active": True,
        "duration": "full_day",
        "skiers": [{"age": 70}]
    }]
    result = process_resort_bookings(groups, 15.0)
    assert result["total_revenue"] == 56.0


def test_regular_adult_with_gear():
    groups = [{
        "is_active": True,
        "duration": "full_day",
        "skiers": [{"age": 30, "gear_rental": True}]
    }]
    result = process_resort_bookings(groups, 15.0)
    assert result["total_revenue"] == 115.0


def test_blackout_override_full_day():
    groups = [{
        "is_active": True,
        "duration": "full_day",
        "skiers": [{
            "age": 30,
            "blackout_override": True,
            "gear_rental": True
        }]
    }]
    result = process_resort_bookings(groups, 15.0)
    assert result["total_revenue"] == 75.0


def test_blackout_override_half_day():
    groups = [{
        "is_active": True,
        "duration": "half_day",
        "skiers": [{
            "age": 30,
            "blackout_override": True
        }]
    }]
    result = process_resort_bookings(groups, 15.0)
    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_SALES"


def test_lodge_locker_fee():
    groups = [{
        "is_active": True,
        "duration": "full_day",
        "includes_lodge_locker": True,
        "skiers": [{"age": 30}]
    }]
    result = process_resort_bookings(groups, 15.0)
    assert result["total_revenue"] == 95.0


def test_audit_review():
    groups = [
        {
            "is_active": True,
            "duration": "unknown",
            "skiers": []
        }
        for _ in range(5)
    ]
    result = process_resort_bookings(groups, 15.0)
    assert result["status"] == "AUDIT_REVIEW"


def test_completed_revenue():
    groups = [{
        "is_active": True,
        "duration": "full_day",
        "skiers": [{"age": 30}, {"age": 30}]
    }]
    result = process_resort_bookings(groups, 15.0)
    assert result == {
        "total_revenue": 160.0,
        "status": "COMPLETED"
    }


# ==========================================
# TESTS FOR check_chairlift_anemometer()
# ==========================================

def test_anemometer_no_data():
    assert check_chairlift_anemometer([]) == "NO_DATA"


def test_anemometer_safe_operation():
    assert check_chairlift_anemometer(
        [[30, 40, 45], [20, 35]]
    ) == "SAFE_OPERATION"


def test_anemometer_single_gust():
    assert check_chairlift_anemometer(
        [[50, 30, 40]]
    ) == "SAFE_OPERATION"


def test_anemometer_two_consecutive_gusts():
    assert check_chairlift_anemometer(
        [[50, 48]]
    ) == "SUSPEND_LIFT"


def test_anemometer_gust_streak_reset():
    assert check_chairlift_anemometer(
        [[50, 30, 50]]
    ) == "SAFE_OPERATION"


def test_anemometer_empty_lift_readings():
    assert check_chairlift_anemometer(
        [[], [30, 40]]
    ) == "SAFE_OPERATION"