import ollama

# -------------------------------
# Character Creation
# -------------------------------

def create_character():

    print("\n====================================")
    print("       CREATE AI CHARACTER")
    print("====================================")

    name = input("Character Name: ")
    age = input("Age: ")
    personality = input("Personality: ")
    occupation = input("Occupation: ")
    power = input("Superpower: ")
    genre = input("Genre/World: ")

    prompt = f"""
Create a fictional character using these details:

Name: {name}
Age: {age}
Personality: {personality}
Occupation: {occupation}
Superpower: {power}
Genre/World: {genre}

Generate:

Character Introduction
Personality
Backstory
Strengths
Weaknesses
Goals
Abilities
Enemy/Rival
Famous Dialogue
Make the character creative and interesting.
"""

    print("\nCreating character...")

    response = ollama.generate(
        model="llama3.2",
        prompt=prompt
    )

    character = response["response"]

    print("\n====================================")
    print("         YOUR AI CHARACTER")
    print("====================================")
    print(character)

    return name, character

# -------------------------------
# Chat With Character
# -------------------------------

def chat_with_character(name, character):

    print("\n====================================")
    print(f"       CHAT WITH {name.upper()}")
    print("====================================")

    print("Type 'exit' to leave the chat.\n")

    while True:

        user_message = input("You: ")

        if user_message.lower() == "exit":
            print("\nLeaving character chat...")
            break

        prompt = f"""
You are roleplaying as the fictional character below.

CHARACTER:
{character}

User message:
{user_message}

Reply as the character.

Stay consistent with the character's personality,
background, abilities and world.

Do not explain that you are an AI.
"""

        response = ollama.generate(
            model="llama3.2",
            prompt=prompt
        )

        print(f"\n{name}: {response['response']}\n")

# -------------------------------
# Main Menu
# -------------------------------

def main():

    name = None
    character = None

    while True:

        print("\n====================================")
        print("        AI CHARACTER STUDIO")
        print("====================================")

        print("1. Create Character")
        print("2. Chat With Character")
        print("3. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":

            name, character = create_character()

        elif choice == "2":

            if character is None:

                print("\nPlease create a character first.")

            else:

                chat_with_character(name, character)

        elif choice == "3":

            print("\nThank you for using AI Character Studio!")
            break

        else:

            print("\nInvalid choice. Please try again.")

# -------------------------------
# Start Program
# -------------------------------

if __name__ == "__main__":
    main()
