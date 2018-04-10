/* fib.g -  Compute fibonacci numbers */

const LAST = 30;            // A constant declaration

// A function declaration
func fibonacci(n int) int {
    if n > 1 {              // Conditionals
        return fibonacci(n-1) + fibonacci(n-2);
    } else {
        return 1;
    }
}

func main() int {
    var n int = 0;            // Variable declaration
    while n < LAST {          // Looping (while)
        print fibonacci(n);   // Printing
        n = n + 1;            // Assignment
     }
     return 0;
}
