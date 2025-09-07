import random

def generate_random_number(start, end):
    """
    Generate a random number between start and end (inclusive).
    """
    return random.randint(start, end)

if __name__ == "__main__":
    # Define the range for random numbers
    start = 1
    end = 100
    
    # Generate a random number
    random_number = generate_random_number(start, end)
    
    # Print the generated random number
    print(f"Generated random number between {start} and {end}: {random_number}")