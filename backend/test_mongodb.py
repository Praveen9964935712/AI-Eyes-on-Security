"""
Test MongoDB Atlas Connection
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
import dns.resolver

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    mongodb_url = os.getenv('MONGODB_URL')
    
    if not mongodb_url:
        print("❌ No MONGODB_URL found in .env file")
        return False
    
    print("🔌 Testing MongoDB Atlas connection...")
    print(f"📍 URL: {mongodb_url[:50]}...")
    
    try:
        # Test DNS resolution first
        print("🌐 Testing DNS resolution...")
        import socket
        hostname = "cluster0.7gifool.mongodb.net"
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS resolution successful: {hostname} -> {ip}")
        
        # Test MongoDB connection
        print("🔗 Testing MongoDB connection...")
        client = MongoClient(
            mongodb_url,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000
        )
        
        # Test the connection
        client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful!")
        
        # Test database operations
        db = client['ai_eyes_security']
        collection = db['test_collection']
        
        # Insert a test document
        result = collection.insert_one({"test": "connection", "timestamp": "2025-10-07"})
        print(f"✅ Test document inserted: {result.inserted_id}")
        
        # Remove test document
        collection.delete_one({"_id": result.inserted_id})
        print("✅ Test document cleaned up")
        
        client.close()
        return True
        
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        print("💡 Try connecting to a different network or check firewall settings")
        return False
    except ConfigurationError as e:
        print(f"❌ MongoDB configuration error: {e}")
        print("💡 Check your MongoDB Atlas connection string")
        return False
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("💡 Check your MongoDB Atlas cluster status and network access")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_mongodb_connection()
    if success:
        print("\n🎉 MongoDB Atlas is ready to use!")
    else:
        print("\n⚠️ MongoDB Atlas connection failed. System will use fallback storage.")