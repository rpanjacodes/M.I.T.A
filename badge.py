# badge.py

# This dictionary maps user IDs to a list of badge emojis and labels.
# You can think of it as assigning custom badges to specific users.

BADGES = {
    # Replace the numbers with actual Discord user IDs
    # Example: 123456789012345678 is the user's Discord ID
    909798528694489098: ["<:bot_contributors:1370416669952049192>", "<:bot_staffdev:1370416272885682240>", "<:beta_tester:1370416186331889674>"],  # This user has two badges
    1174837648318283817: ["<:beta_tester:1370416186331889674>"],      
    1178192889344438383: ["<:beta_tester:1370416186331889674>"]
    # Add more users and their badges below as needed
}

# This function gets the badges for a given user ID.
# If the user has no badges, it returns an empty list.
def get_badges(user_id: int):
    return BADGES.get(user_id, [])
