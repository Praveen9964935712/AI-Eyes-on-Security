#!/usr/bin/env python3
"""
MongoDB Atlas Setup Helper for AI Eyes Security System
"""
import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with MongoDB Atlas configuration"""
    print("🔧 MongoDB Atlas Setup Helper")
    print("=" * 50)
    
    # Get MongoDB Atlas connection string
    print("\n📋 Please provide your MongoDB Atlas connection string:")
    print("   (Example: mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/)")
    
    mongodb_url = input("MongoDB URL: ").strip()
    
    if not mongodb_url:
        print("❌ MongoDB URL is required!")
        return False
    
    # Add database name if not present
    if '?' in mongodb_url:
        # Has query parameters
        if '/ai_eyes_security?' not in mongodb_url:
            mongodb_url = mongodb_url.replace('/?', '/ai_eyes_security?')
    else:
        # No query parameters
        if not mongodb_url.endswith('/'):
            mongodb_url += '/'
        mongodb_url += 'ai_eyes_security'
    
    # Create .env content
    env_content = f"""# MongoDB Atlas Configuration for AI Eyes Security System
MONGODB_URL={mongodb_url}
DATABASE_NAME=ai_eyes_security

# Flask settings
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=true

# Storage settings
STORAGE_PATH=./storage
MAX_FILE_AGE_DAYS=30
MAX_STORAGE_SIZE_MB=1000
"""
    
    # Write .env file
    env_path = Path(__file__).parent / '.env'
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Created .env file at: {env_path}")
        print("\n🎉 MongoDB Atlas configuration complete!")
        print("\n🚀 Next steps:")
        print("   1. Restart your backend server")
        print("   2. The system will automatically connect to MongoDB Atlas")
        print("   3. Check the console for connection success message")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_connection():
    """Test MongoDB connection"""
    try:
        from dotenv import load_dotenv
        from pymongo import MongoClient
        
        load_dotenv()
        mongodb_url = os.getenv('MONGODB_URL')
        
        if not mongodb_url:
            print("❌ No MongoDB URL found in .env file")
            return False
        
        print("🔍 Testing MongoDB connection...")
        client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        
        print("✅ MongoDB connection successful!")
        
        # List databases
        db_list = client.list_database_names()
        print(f"📊 Available databases: {db_list}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Check your:")
        print("   - MongoDB Atlas connection string")
        print("   - Network access settings (IP whitelist)")
        print("   - Database user credentials")
        return False

def main():
    """Main setup function"""
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_connection()
        return
    
    print("🌟 Welcome to AI Eyes Security System MongoDB Setup!")
    print("\n📋 Setup Menu:")
    print("   1. Configure MongoDB Atlas (.env file)")
    print("   2. Test MongoDB connection")
    print("   3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        create_env_file()
    elif choice == '2':
        test_connection()
    elif choice == '3':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid option. Please choose 1, 2, or 3.")

if __name__ == '__main__':
    main()