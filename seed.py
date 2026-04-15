from app import app
from models import db, User, JournalEntry
from datetime import datetime, timedelta
import random

def seed_database():
    
    with app.app_context():
       
        db.drop_all()
        db.create_all()
        
      
        users = []
        sample_users = [
            {'username': 'Jules', 'email': 'jules@gmail.com', 'password': 'password123'},
            {'username': 'Nick', 'email': 'nick@gmail.com', 'password': 'password123'},
            {'username': 'charlie', 'email': 'charlie@example.com', 'password': 'password123'}
        ]
        
        for user_data in sample_users:
            user = User(username=user_data['username'], email=user_data['email'])
            user.set_password(user_data['password'])
            db.session.add(user)
            users.append(user)
        
        db.session.commit()
        
        
        moods = ['Happy', 'Sad', 'Excited', 'Anxious', 'Calm', 'Grateful', 'Tired']
        titles = [
            'First Day of Spring',
            'Work Project Completed',
            'Weekend Adventures',
            'Reflections on Growth',
            'Goals for Next Month',
            'Gratitude List',
            'Challenges Overcome'
        ]
        
        for user in users:
          
            num_entries = random.randint(15, 20)
            for i in range(num_entries):
                days_ago = random.randint(0, 30)
                entry = JournalEntry(
                    title=f"{random.choice(titles)} - Entry {i+1}",
                    content=f"This is a sample journal entry for {user.username}. " * random.randint(2, 5),
                    mood=random.choice(moods),
                    user_id=user.id,
                    created_at=datetime.utcnow() - timedelta(days=days_ago)
                )
                db.session.add(entry)
        
        db.session.commit()
        print(f"Database seeded successfully!")
        print(f"Created {len(users)} users")
        print(f"Created {JournalEntry.query.count()} journal entries")
        
     
        print("\nTest User Credentials:")
        for user in users:
            print(f"Username: {user.username}, Password: password123")

if __name__ == '__main__':
    seed_database()