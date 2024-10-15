int i = 2;
for (i; i<=20; i+=2)
    Console.WriteLine(i);

int a=Console.ReadLine();

while (a!=1) {
    if (a%2==0) {
        a/=2
    }
    else {
        a*=3
        a+=1
    }
}