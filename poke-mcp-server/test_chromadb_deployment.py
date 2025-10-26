#!/usr/bin/env python3
"""
Test script for deployed ChromaDB at https://memary-chromadb.ngrok-free.app
Tests all available API endpoints without requiring local vector-store setup
"""
import requests
import json
import time
from colorama import init, Fore, Style

init(autoreset=True)

# Deployed ChromaDB URL
BASE_URL = "https://memary-chromadb.ngrok-free.app"

# Headers for ngrok free tier (bypass browser warning)
HEADERS = {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true"
}

def print_section(title):
    """Print formatted section header"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{title}")
    print(f"{'='*70}{Style.RESET_ALL}\n")

def print_success(msg):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")

def print_error(msg):
    """Print error message"""
    print(f"{Fore.RED}✗ {msg}{Style.RESET_ALL}")

def print_info(msg):
    """Print info message"""
    print(f"{Fore.YELLOW}ℹ {msg}{Style.RESET_ALL}")

def test_connection():
    """Test basic connectivity to ChromaDB"""
    print_section("TEST 1: Connection & Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/", headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"ChromaDB is accessible!")
            print(f"   Service: {data.get('service', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
            return True
        else:
            print_error(f"Connection failed with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Connection error: {str(e)}")
        return False

def test_list_endpoints():
    """List all available API endpoints"""
    print_section("TEST 2: Available API Endpoints")
    
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            openapi = response.json()
            paths = openapi.get('paths', {})
            
            print_success(f"Found {len(paths)} endpoints:")
            for path, methods in paths.items():
                method_list = ', '.join(methods.keys()).upper()
                print(f"   {method_list:10} {path}")
            
            return paths
        else:
            print_error(f"Failed to get API spec")
            return {}
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return {}

def test_get_statistics():
    """Get storage statistics"""
    print_section("TEST 3: Storage Statistics")
    
    try:
        response = requests.get(f"{BASE_URL}/statistics", headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            print_success("Statistics retrieved:")
            print(json.dumps(stats, indent=2))
            return stats
        else:
            print_error(f"Failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_store_memory():
    """Test storing a memory/note"""
    print_section("TEST 4: Store Memory (Add Note)")
    
    test_memory = {
        "text": "My keys are usually on the kitchen counter",
        "metadata": {
            "priority": "high",
            "tags": ["keys", "location"],
            "test": True
        }
    }
    
    try:
        # Try /store_text endpoint
        response = requests.post(
            f"{BASE_URL}/store_text",
            headers=HEADERS,
            json=test_memory,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Memory stored successfully!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return result
        else:
            print_error(f"Failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try alternative endpoint /store
            print_info("Trying /store endpoint...")
            response = requests.post(
                f"{BASE_URL}/store",
                headers=HEADERS,
                json=test_memory,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print_success("Memory stored via /store!")
                print(f"Response: {json.dumps(result, indent=2)}")
                return result
            else:
                print_error(f"Also failed: {response.status_code}")
                print(f"Response: {response.text}")
            
            return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_search_memory():
    """Test searching for memories"""
    print_section("TEST 5: Search Memory")
    
    search_query = "where are my keys?"
    
    try:
        # Try /search endpoint
        response = requests.get(
            f"{BASE_URL}/search",
            headers=HEADERS,
            params={"query": search_query},
            timeout=10
        )
        
        if response.status_code == 200:
            results = response.json()
            print_success(f"Search completed!")
            print(f"Query: '{search_query}'")
            print(f"Results: {json.dumps(results, indent=2)}")
            return results
        else:
            print_error(f"Failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_get_memories():
    """Test retrieving all memories"""
    print_section("TEST 6: Get All Memories")
    
    try:
        response = requests.get(f"{BASE_URL}/memories", headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            memories = response.json()
            print_success(f"Retrieved memories!")
            
            if isinstance(memories, list):
                print(f"Total memories: {len(memories)}")
                if memories:
                    print("\nFirst few memories:")
                    for i, mem in enumerate(memories[:3], 1):
                        print(f"\n  Memory {i}:")
                        print(f"    {json.dumps(mem, indent=6)}")
            else:
                print(f"Response: {json.dumps(memories, indent=2)}")
            
            return memories
        else:
            print_error(f"Failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_track_item():
    """Test tracking an item"""
    print_section("TEST 7: Track Item")
    
    item_data = {
        "item_name": "keys",
        "location": "kitchen counter",
        "description": "silver keys on a blue keychain"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/track_item",
            headers=HEADERS,
            json=item_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Item tracked successfully!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return result
        else:
            print_error(f"Failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_find_item():
    """Test finding a tracked item"""
    print_section("TEST 8: Find Item")
    
    item_name = "keys"
    
    try:
        response = requests.get(
            f"{BASE_URL}/find/{item_name}",
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Found item: {item_name}")
            print(f"Response: {json.dumps(result, indent=2)}")
            return result
        else:
            print_error(f"Failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_get_tracked_items():
    """Get all tracked items"""
    print_section("TEST 9: Get All Tracked Items")
    
    try:
        response = requests.get(
            f"{BASE_URL}/tracked_items",
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            items = response.json()
            print_success("Retrieved tracked items!")
            print(f"Response: {json.dumps(items, indent=2)}")
            return items
        else:
            print_error(f"Failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def main():
    """Run all tests"""
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print("ChromaDB Deployment Test Suite")
    print(f"URL: {BASE_URL}")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    results = {}
    
    # Test 1: Connection
    results['connection'] = test_connection()
    if not results['connection']:
        print_error("\n❌ Cannot connect to ChromaDB. Please check:")
        print("   1. Is ngrok tunnel running?")
        print("   2. Is the ChromaDB server running?")
        print("   3. Is the URL correct?")
        return
    
    time.sleep(0.5)
    
    # Test 2: List endpoints
    endpoints = test_list_endpoints()
    results['endpoints'] = bool(endpoints)
    time.sleep(0.5)
    
    # Test 3: Statistics
    results['statistics'] = test_get_statistics() is not None
    time.sleep(0.5)
    
    # Test 4: Store memory
    results['store'] = test_store_memory() is not None
    time.sleep(0.5)
    
    # Test 5: Search
    results['search'] = test_search_memory() is not None
    time.sleep(0.5)
    
    # Test 6: Get memories
    results['memories'] = test_get_memories() is not None
    time.sleep(0.5)
    
    # Test 7: Track item
    results['track'] = test_track_item() is not None
    time.sleep(0.5)
    
    # Test 8: Find item
    results['find'] = test_find_item() is not None
    time.sleep(0.5)
    
    # Test 9: Get tracked items
    results['tracked_items'] = test_get_tracked_items() is not None
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, success in results.items():
        status = f"{Fore.GREEN}✓ PASS" if success else f"{Fore.RED}✗ FAIL"
        print(f"{status} - {test_name.replace('_', ' ').title()}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Result: {passed}/{total} tests passed{Style.RESET_ALL}")
    
    if passed == total:
        print(f"{Fore.GREEN}\n🎉 All tests passed! ChromaDB is fully functional.{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}📝 Next Steps:{Style.RESET_ALL}")
        print("   1. Update MCP server to use the correct endpoints")
        print("   2. Test MCP server with real ChromaDB")
        print("   3. Deploy to Render")
    else:
        print(f"{Fore.YELLOW}\n⚠️  Some tests failed.{Style.RESET_ALL}")
        print("Review the errors above and check:")
        print("   - API endpoints match what's deployed")
        print("   - Request payloads are correct")
        print("   - Server is fully initialized")

if __name__ == "__main__":
    main()


