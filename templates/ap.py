"""import math

score=input("Zadejte skóre jednotlivých studentů oddělené čárkou bez mezery")
score=score.split(",")

sum=0

max=-math.inf

for score_one in score:
    sum+=int(score_one)

print(f"{sum/len(score)}")

for score_one in score:
    if int(score_one)>max:
        max=int(score_one)

print(max)"""

"""sum=0

for i in range(1,101):
    if i%5==0 and i%3==0:
        print("Fizzbuzz")
    elif i%3==0:
        print("Fizz")
    elif i%5==0:
        print("Buzz")
    else:
        print(i)

"""
"""import random

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
special_char = ['%', '#', '$', '!', '&', '(', ')', '*', '+', '?']

letters_count=int(input("Kolik písmen chcete ve jméně"))
numbers_count=int(input("Kolik čísel chcete ve jméně"))
special_char_count=int(input("Kolik speciálních znaků chcete ve jméně"))

password=""

for i in range(0,letters_count):
    password+=(random.choice(letters))

for j in range(0,numbers_count):
    password+=(random.choice(numbers))

for k in range(0,special_char_count):
    password+=(random.choice(special_char))

print(password)"""

"""import random

character=["Harry","Hermiona","Ron","Albus","Draco"]

current_character=random.choice(character)

guess=input("Hádej postavu")

count=3

while guess!=current_character and count!=0:
    print("Ne!")
    guess=input("Hádej postavu")
    count-=1


if count==0:
    print("Prohrál jsi")
else:

    print("Správně!")"""

"""def vymalovat(a : int, b :int ):
    s=a*b
    s/=5
    return f"Budete potřebovat {s.__ceil__()} kusů plechovek"

a=int(input("Zadejte a"))
b=int(input("Zadejte b"))


print(vymalovat(a,b))"""

"""a=int(input("Zadej číslo"))

counter=0

for i in range(1,a+1):
    if a%i==0:
        counter+=1

if counter==2:
    print("Číslo je prvočíslo")
else:
    print("Není prvočíslo")"""

students_results = {
    "Harry" : 85,
    "Ron" : 71,
    "Hermione" : 98,
    "Draco" : 69
}

for key in students_results:
    if 91 <= students_results[key] <= 100:
        print("Exc")
    elif 81 <= students_results[key] <= 90:
        print("Vyn")
    elif 71 <= students_results[key] <= 80:
        print("Spln")
    else:
        print("Nespln")