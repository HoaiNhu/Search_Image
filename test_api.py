"""
Simple test script to verify the image search functionality.
"""
import requests
import os


def test_health_check():
    """Test health check endpoint."""
    print("\n=== Testing Health Check ===")
    response = requests.get("http://localhost:8001/api/v1/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_search_by_url():
    """Test search by URL endpoint."""
    print("\n=== Testing Search by URL ===")
    
    # Example product image URL from your database
    test_url = "https://res.cloudinary.com/dlyl41lgq/image/upload/v1735795001/products/file_u9ksse.jpg"
    
    response = requests.post(
        "http://localhost:8001/api/v1/search/url",
        params={
            "image_url": test_url,
            "top_k": 5,
            "threshold": 0.5
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        results = response.json()
        print(f"Found {len(results)} similar products")
        for i, result in enumerate(results, 1):
            print(f"\nRank {i}:")
            print(f"  Product: {result['product']['productName']}")
            print(f"  Price: {result['product']['productPrice']}")
            print(f"  Similarity: {result['similarity_score']:.4f}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200


def test_search_by_image(image_path: str):
    """Test search by image upload endpoint."""
    print("\n=== Testing Search by Image Upload ===")
    
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        return False
    
    with open(image_path, 'rb') as f:
        files = {'file': ('test_image.jpg', f, 'image/jpeg')}
        response = requests.post(
            "http://localhost:8001/api/v1/search/image",
            files=files,
            params={
                "top_k": 5,
                "threshold": 0.5
            }
        )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        results = response.json()
        print(f"Found {len(results)} similar products")
        for i, result in enumerate(results, 1):
            print(f"\nRank {i}:")
            print(f"  Product: {result['product']['productName']}")
            print(f"  Price: {result['product']['productPrice']}")
            print(f"  Similarity: {result['similarity_score']:.4f}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200


def main():
    """Run all tests."""
    print("=" * 50)
    print("Image Search API Test Suite")
    print("=" * 50)
    
    # Test 1: Health check
    test1_passed = test_health_check()
    
    # Test 2: Search by URL
    test2_passed = test_search_by_url()
    
    # Test 3: Search by image upload (optional - requires image file)
    # Uncomment and provide image path if you want to test upload
    # test3_passed = test_search_by_image("path/to/your/test_image.jpg")
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"  Health Check: {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"  Search by URL: {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    print("=" * 50)


if __name__ == "__main__":
    main()
