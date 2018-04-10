/* fact.g - Factorials */

func main() int {
    var fact int = 1;
    var n int = 1;
    while n < 10 {
       fact = fact * n;
       print fact;
       n = n + 1;
    }
    return 0;
}

