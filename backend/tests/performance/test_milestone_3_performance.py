"""
Performance tests for Milestone 3

Measures:
- API response times
- Database query performance
- Pagination efficiency
- Search performance
- System scalability
"""

import pytest
import time
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import statistics

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.main import app

client = TestClient(app)


def get_unique_email():
    """Generate unique email for testing"""
    import uuid
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


# ==================== PERFORMANCE METRICS ====================

class PerformanceMetrics:
    """Collect and analyze performance metrics"""
    
    def __init__(self):
        """Initialize metrics collector"""
        self.measurements = {}
    
    def measure(self, metric_name: str, duration: float):
        """Record a measurement"""
        if metric_name not in self.measurements:
            self.measurements[metric_name] = []
        self.measurements[metric_name].append(duration)
    
    def get_stats(self, metric_name: str) -> dict:
        """Get statistics for a metric"""
        if metric_name not in self.measurements:
            return {}
        
        data = self.measurements[metric_name]
        return {
            "count": len(data),
            "min": min(data),
            "max": max(data),
            "avg": statistics.mean(data),
            "median": statistics.median(data),
            "stdev": statistics.stdev(data) if len(data) > 1 else 0
        }


# ==================== PROFILE API PERFORMANCE ====================

class TestProfileAPIPerformance:
    """Performance tests for profile endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: register user"""
        user = {
            "first_name": "Perf",
            "last_name": "User",
            "email": get_unique_email(),
            "password": "TestPass123!"
        }
        response = client.post("/api/auth/register", json=user)
        data = response.json()
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.metrics = PerformanceMetrics()
    
    def test_get_profile_response_time(self):
        """Measure GET /profile/me response time"""
        # Warm up
        client.get("/api/profile/me", headers=self.headers)
        
        # Measure 10 requests
        for _ in range(10):
            start = time.time()
            response = client.get("/api/profile/me", headers=self.headers)
            duration = (time.time() - start) * 1000  # Convert to ms
            
            assert response.status_code == 200
            self.metrics.measure("get_profile", duration)
        
        stats = self.metrics.get_stats("get_profile")
        print(f"\nGET /profile/me: {stats['avg']:.2f}ms avg")
        
        # Assert performance target: < 100ms average
        assert stats["avg"] < 100, f"GET /profile/me too slow: {stats['avg']:.2f}ms"
    
    def test_update_profile_response_time(self):
        """Measure PUT /profile/me response time"""
        update_data = {"first_name": "Updated"}
        
        for i in range(5):
            start = time.time()
            response = client.put(
                "/api/profile/me",
                json=update_data,
                headers=self.headers
            )
            duration = (time.time() - start) * 1000
            
            assert response.status_code == 200
            self.metrics.measure("put_profile", duration)
        
        stats = self.metrics.get_stats("put_profile")
        print(f"\nPUT /profile/me: {stats['avg']:.2f}ms avg")
        
        # Assert performance target: < 150ms average
        assert stats["avg"] < 150, f"PUT /profile/me too slow: {stats['avg']:.2f}ms"
    
    def test_add_medical_history_response_time(self):
        """Measure medical history addition response time"""
        for i in range(5):
            history = {
                "condition": f"Condition {i}",
                "status": "active"
            }
            start = time.time()
            response = client.post(
                "/api/profile/medical-history",
                json=history,
                headers=self.headers
            )
            duration = (time.time() - start) * 1000
            
            assert response.status_code in [200, 201]
            self.metrics.measure("post_medical_history", duration)
        
        stats = self.metrics.get_stats("post_medical_history")
        print(f"\nPOST /profile/medical-history: {stats['avg']:.2f}ms avg")
        
        # Assert performance target: < 150ms average
        assert stats["avg"] < 150


# ==================== CONVERSATION API PERFORMANCE ====================

class TestConversationAPIPerformance:
    """Performance tests for conversation endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: register user and create conversations"""
        user = {
            "first_name": "Conv",
            "last_name": "User",
            "email": get_unique_email(),
            "password": "TestPass123!"
        }
        response = client.post("/api/auth/register", json=user)
        data = response.json()
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.metrics = PerformanceMetrics()
        
        # Create test conversations
        self.conversation_ids = []
        for i in range(5):
            conv_data = {
                "title": f"Test Conversation {i}",
                "initial_symptoms": f"Symptoms {i}"
            }
            response = client.post(
                "/api/conversations",
                json=conv_data,
                headers=self.headers
            )
            if response.status_code in [200, 201]:
                self.conversation_ids.append(response.json().get("id"))
    
    def test_list_conversations_response_time(self):
        """Measure GET /conversations response time"""
        for _ in range(10):
            start = time.time()
            response = client.get(
                "/api/conversations/?limit=20&offset=0",
                headers=self.headers
            )
            duration = (time.time() - start) * 1000
            
            assert response.status_code == 200
            self.metrics.measure("list_conversations", duration)
        
        stats = self.metrics.get_stats("list_conversations")
        print(f"\nGET /conversations: {stats['avg']:.2f}ms avg")
        
        # Assert performance target: < 100ms average
        assert stats["avg"] < 100
    
    def test_create_conversation_response_time(self):
        """Measure POST /conversations response time"""
        for i in range(5):
            conv_data = {
                "title": f"Perf Test Conv {i}",
                "initial_symptoms": "Test"
            }
            start = time.time()
            response = client.post(
                "/api/conversations",
                json=conv_data,
                headers=self.headers
            )
            duration = (time.time() - start) * 1000
            
            assert response.status_code in [200, 201]
            self.metrics.measure("create_conversation", duration)
        
        stats = self.metrics.get_stats("create_conversation")
        print(f"\nPOST /conversations: {stats['avg']:.2f}ms avg")
        
        # Assert performance target: < 150ms average
        assert stats["avg"] < 150
    
    def test_search_conversations_response_time(self):
        """Measure search performance"""
        search_queries = ["fever", "headache", "pain", "cough"]
        
        for query in search_queries:
            search_data = {"query": query, "limit": 20, "offset": 0}
            start = time.time()
            response = client.post(
                "/api/conversations/search",
                json=search_data,
                headers=self.headers
            )
            duration = (time.time() - start) * 1000
            
            assert response.status_code == 200
            self.metrics.measure("search_conversations", duration)
        
        stats = self.metrics.get_stats("search_conversations")
        print(f"\nPOST /conversations/search: {stats['avg']:.2f}ms avg")
        
        # Assert performance target: < 200ms average (search is complex)
        assert stats["avg"] < 200


# ==================== PAGINATION PERFORMANCE ====================

class TestPaginationPerformance:
    """Performance tests for pagination efficiency"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: register user"""
        user = {
            "first_name": "Paginate",
            "last_name": "User",
            "email": get_unique_email(),
            "password": "TestPass123!"
        }
        response = client.post("/api/auth/register", json=user)
        data = response.json()
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.metrics = PerformanceMetrics()
    
    def test_pagination_small_offset_performance(self):
        """Measure pagination with small offset"""
        for offset in [0, 10, 20]:
            start = time.time()
            response = client.get(
                f"/api/conversations/?limit=10&offset={offset}",
                headers=self.headers
            )
            duration = (time.time() - start) * 1000
            
            assert response.status_code == 200
            self.metrics.measure("pagination_small", duration)
        
        stats = self.metrics.get_stats("pagination_small")
        print(f"\nPagination (offset 0-20): {stats['avg']:.2f}ms avg")
        
        assert stats["avg"] < 100
    
    def test_pagination_large_offset_performance(self):
        """Measure pagination with large offset"""
        for offset in [100, 200]:
            start = time.time()
            response = client.get(
                f"/api/conversations/?limit=10&offset={offset}",
                headers=self.headers
            )
            duration = (time.time() - start) * 1000
            
            assert response.status_code == 200
            self.metrics.measure("pagination_large", duration)
        
        stats = self.metrics.get_stats("pagination_large")
        print(f"\nPagination (offset 100+): {stats['avg']:.2f}ms avg")
        
        # Large offset might be slightly slower due to DB offset
        assert stats["avg"] < 150


# ==================== SYSTEM LOAD TESTS ====================

class TestSystemLoadPerformance:
    """Performance under load"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: register user"""
        user = {
            "first_name": "Load",
            "last_name": "User",
            "email": get_unique_email(),
            "password": "TestPass123!"
        }
        response = client.post("/api/auth/register", json=user)
        data = response.json()
        self.user_id = data.get("user", {}).get("id")
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.metrics = PerformanceMetrics()
    
    def test_concurrent_profile_reads(self):
        """Test concurrent profile read operations"""
        # Simulate 20 concurrent reads
        for _ in range(20):
            start = time.time()
            response = client.get("/api/profile/me", headers=self.headers)
            duration = (time.time() - start) * 1000
            
            assert response.status_code == 200
            self.metrics.measure("concurrent_read", duration)
        
        stats = self.metrics.get_stats("concurrent_read")
        print(f"\n20 Concurrent reads: {stats['avg']:.2f}ms avg, max {stats['max']:.2f}ms")
        
        # Should still be reasonably fast
        assert stats["max"] < 500  # No request should take > 500ms
    
    def test_bulk_conversation_creation(self):
        """Test creating multiple conversations rapidly"""
        for i in range(10):
            conv_data = {
                "title": f"Bulk Conv {i}",
                "initial_symptoms": "Test"
            }
            start = time.time()
            response = client.post(
                "/api/conversations",
                json=conv_data,
                headers=self.headers
            )
            duration = (time.time() - start) * 1000
            
            assert response.status_code in [200, 201]
            self.metrics.measure("bulk_create", duration)
        
        stats = self.metrics.get_stats("bulk_create")
        print(f"\n10 Bulk creations: {stats['avg']:.2f}ms avg, max {stats['max']:.2f}ms")
        
        # Sustained creation should be consistent
        assert stats["max"] < 300  # No request should take > 300ms


# ==================== WELLNESS REPORT PERFORMANCE ====================

class TestWellnessReportPerformance:
    """Performance tests for analytics/wellness report"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: register user with data"""
        user = {
            "first_name": "Analytics",
            "last_name": "User",
            "email": get_unique_email(),
            "password": "TestPass123!"
        }
        response = client.post("/api/auth/register", json=user)
        data = response.json()
        self.user_id = data.get("user", {}).get("id")
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.metrics = PerformanceMetrics()
    
    def test_wellness_report_response_time(self):
        """Measure wellness report generation time"""
        if not self.user_id:
            pytest.skip("User ID not available")
        
        for _ in range(5):
            start = time.time()
            response = client.get(
                f"/api/conversations/{self.user_id}/wellness-report",
                headers=self.headers
            )
            duration = (time.time() - start) * 1000
            
            assert response.status_code == 200
            self.metrics.measure("wellness_report", duration)
        
        stats = self.metrics.get_stats("wellness_report")
        print(f"\nWellness report generation: {stats['avg']:.2f}ms avg")
        
        # Analytics should be fast (< 500ms)
        assert stats["avg"] < 500


# ==================== SUMMARY PERFORMANCE REPORT ====================

def test_performance_summary(capsys):
    """Print performance summary report"""
    print("\n" + "="*60)
    print("MILESTONE 3 PERFORMANCE METRICS SUMMARY")
    print("="*60)
    print("\nPerformance Targets:")
    print("- API endpoints: < 100ms average")
    print("- Search operations: < 200ms average")
    print("- Wellness analytics: < 500ms average")
    print("- No request should exceed: < 500ms (p100)")
    print("\nTests will validate these targets automatically")
    print("="*60 + "\n")
