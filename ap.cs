int x = 5;
while (x < 10) { 
    Console.WriteLine(x);
    x++;
} 


if (a%7==0 && a%5==0) {
    System.Console.WriteLine("Číslo je dělitelné pěti i sedmi");
} else if (a%7==0) {
    System.Console.WriteLine("Čístlo je dělitelné sedmi");
} else if (a%5==0) {
    System.Console.WriteLine("Číslo je dělitelné pěti");
} else {
    System.Console.WriteLine("Číslo není dělitelné pěti ani sedmi");
}


switch(a) {
    case 1:
        System.Console.WriteLine("Proměnná a je rovna 1");
        break;
    case 2:
        System.Console.WriteLine("Proměnná a je rovna 2");
        break;
    case 3:
        System.Console.WriteLine("Proměnná a je rovna 3");
        break;
    default:
        System.Console.WriteLine("Proměnná a nepatří do množiny {1,2,3}");
        break;
}

int i = 2;
for (i; i <= 20; i += 2) {
    System.Console.WriteLine(i);
}

while (a != 1) {
    if (a%2 == 0) {
        a /= 2;
    }
    else {
        a *= 3;
        a += 1;
    }
}

while(true) {
    System.Console.WriteLine("Ahoj");
}

do {
    System.Console.WriteLine("Ahoj");
} while (false);

List<int> list = new List<int> ();
list.Add(5);
list.Remove(5); // list.RemoveAt(0);

int[] array = new int[10];
array[0] = 5;

