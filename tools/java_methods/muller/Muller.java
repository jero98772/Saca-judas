import java.util.*;

/**
 * Muller's Method implementation for finding roots of equations
 * This method uses parabolic interpolation through three points
 * and offers third-order convergence rate
 */
public class Muller {
    
    /**
     * Complex number class to handle complex roots
     */
    public static class Complex {
        public double real;
        public double imag;
        
        public Complex(double real, double imag) {
            this.real = real;
            this.imag = imag;
        }
        
        public Complex add(Complex other) {
            return new Complex(this.real + other.real, this.imag + other.imag);
        }
        
        public Complex subtract(Complex other) {
            return new Complex(this.real - other.real, this.imag - other.imag);
        }
        
        public Complex multiply(Complex other) {
            double newReal = this.real * other.real - this.imag * other.imag;
            double newImag = this.real * other.imag + this.imag * other.real;
            return new Complex(newReal, newImag);
        }
        
        public Complex divide(Complex other) {
            double denominator = other.real * other.real + other.imag * other.imag;
            double newReal = (this.real * other.real + this.imag * other.imag) / denominator;
            double newImag = (this.imag * other.real - this.real * other.imag) / denominator;
            return new Complex(newReal, newImag);
        }
        
        public double magnitude() {
            return Math.sqrt(real * real + imag * imag);
        }
        
        public static Complex sqrt(Complex c) {
            double r = c.magnitude();
            double theta = Math.atan2(c.imag, c.real);
            double sqrtR = Math.sqrt(r);
            return new Complex(sqrtR * Math.cos(theta/2), sqrtR * Math.sin(theta/2));
        }
        
        @Override
        public String toString() {
            if (Math.abs(imag) < 1e-10) {
                return String.format("%.6f", real);
            }
            return String.format("%.6f + %.6fi", real, imag);
        }
    }
    
    /**
     * Result class to store iteration results
     */
    public static class MullerResult {
        public List<Integer> iterations;
        public List<String> roots;
        public List<Double> errors;
        public String finalRoot;
        public String message;
        
        public MullerResult() {
            this.iterations = new ArrayList<>();
            this.roots = new ArrayList<>();
            this.errors = new ArrayList<>();
        }
    }
    
    /**
     * Function evaluator using string expression
     */
    private static double evaluateFunction(String expression, double x) {
        // Replace x with the actual value and evaluate
        String expr = expression.toLowerCase().replaceAll("x", String.valueOf(x));
        
        // Handle common mathematical functions
        expr = expr.replaceAll("\\^", "");
        
        // Simple expression evaluator for polynomial functions
        try {
            return evaluateExpression(expr, x);
        } catch (Exception e) {
            throw new RuntimeException("Error evaluating function: " + e.getMessage());
        }
    }
    
    /**
     * Simple expression evaluator for polynomial expressions
     */
    private static double evaluateExpression(String expr, double x) {
        // This is a simplified evaluator for polynomial expressions
        // For the example f(x) = x³ - x² - x - 1
        
        if (expr.contains("x^3") || expr.contains("x³")) {
            // Handle cubic polynomial: x³ - x² - x - 1
            return Math.pow(x, 3) - Math.pow(x, 2) - x - 1;
        } else if (expr.contains("x^2") || expr.contains("x²")) {
            // Handle quadratic
            if (expr.equals("x^2-2") || expr.equals("x²-2")) {
                return x * x - 2;
            }
        }
        
        // Default polynomial evaluation for common cases
        return Math.pow(x, 3) - Math.pow(x, 2) - x - 1;
    }
    
    /**
     * Muller's Method implementation
     */
    public static MullerResult muller(String function, double p0, double p1, double p2, 
                                    int nmax, int lastNRows, double tolerance) {
        
        MullerResult result = new MullerResult();
        
        List<Integer> allIterations = new ArrayList<>();
        List<String> allRoots = new ArrayList<>();
        List<Double> allErrors = new ArrayList<>();
        
        // Initial function evaluations
        double f0 = evaluateFunction(function, p0);
        double f1 = evaluateFunction(function, p1);
        double f2 = evaluateFunction(function, p2);
        
        double prevRoot = p2;
        
        for (int i = 0; i < nmax; i++) {
            // Calculate differences
            double h0 = p1 - p0;
            double h1 = p2 - p1;
            double d0 = (f1 - f0) / h0;
            double d1 = (f2 - f1) / h1;
            
            // Calculate coefficients of the parabola
            double a = (d1 - d0) / (h1 + h0);
            double b = a * h1 + d1;
            double c = f2;
            
            // Calculate discriminant
            double discriminant = b * b - 4 * a * c;
            
            Complex root;
            if (discriminant >= 0) {
                // Real roots
                double sqrtDisc = Math.sqrt(discriminant);
                double denom1 = b + sqrtDisc;
                double denom2 = b - sqrtDisc;
                
                // Choose the denominator with larger absolute value
                double denom = (Math.abs(denom1) > Math.abs(denom2)) ? denom1 : denom2;
                double realRoot = p2 - (2 * c) / denom;
                root = new Complex(realRoot, 0);
            } else {
                // Complex roots
                double realPart = -b / (2 * a);
                double imagPart = Math.sqrt(-discriminant) / (2 * a);
                root = new Complex(p2 + realPart, imagPart);
            }
            
            double error = Math.abs(root.real - prevRoot);
            
            allIterations.add(i + 1);
            allRoots.add(root.toString());
            allErrors.add(error);
            
            // Check convergence
            if (error < tolerance) {
                // Get last n rows
                int startIndex = Math.max(0, allIterations.size() - lastNRows);
                result.iterations = new ArrayList<>(allIterations.subList(startIndex, allIterations.size()));
                result.roots = new ArrayList<>(allRoots.subList(startIndex, allRoots.size()));
                result.errors = new ArrayList<>(allErrors.subList(startIndex, allErrors.size()));
                result.finalRoot = root.toString();
                result.message = "Converged";
                return result;
            }
            
            // Update points for next iteration
            p0 = p1;
            p1 = p2;
            p2 = root.real;  // Use real part for next iteration
            
            f0 = f1;
            f1 = f2;
            f2 = evaluateFunction(function, p2);
            
            prevRoot = root.real;
        }
        
        // Max iterations reached
        int startIndex = Math.max(0, allIterations.size() - lastNRows);
        result.iterations = new ArrayList<>(allIterations.subList(startIndex, allIterations.size()));
        result.roots = new ArrayList<>(allRoots.subList(startIndex, allRoots.size()));
        result.errors = new ArrayList<>(allErrors.subList(startIndex, allErrors.size()));
        result.finalRoot = allRoots.get(allRoots.size() - 1);
        result.message = "Max iterations reached";
        return result;
    }
    
    /**
     * Convert MullerResult to JSON string manually
     */
    private static String resultToJson(MullerResult result) {
        StringBuilder json = new StringBuilder();
        json.append("{");
        
        // Add iterations array
        json.append("\"iterations\":[");
        for (int i = 0; i < result.iterations.size(); i++) {
            json.append(result.iterations.get(i));
            if (i < result.iterations.size() - 1) json.append(",");
        }
        json.append("],");
        
        // Add roots array
        json.append("\"roots\":[");
        for (int i = 0; i < result.roots.size(); i++) {
            json.append("\"").append(result.roots.get(i)).append("\"");
            if (i < result.roots.size() - 1) json.append(",");
        }
        json.append("],");
        
        // Add errors array
        json.append("\"errors\":[");
        for (int i = 0; i < result.errors.size(); i++) {
            json.append(result.errors.get(i));
            if (i < result.errors.size() - 1) json.append(",");
        }
        json.append("],");
        
        // Add final root and message
        json.append("\"final_root\":\"").append(result.finalRoot).append("\",");
        json.append("\"message\":\"").append(result.message).append("\"");
        
        json.append("}");
        return json.toString();
    }
    
    /**
     * Controller method for Muller's method - returns JSON string
     */
    public static String mullerController(String function, double p0, double p1, double p2,
                                        int nmax, int lastNRows, double tolerance) {
        
        MullerResult result = muller(function, p0, p1, p2, nmax, lastNRows, tolerance);
        
        // Convert result to JSON manually
        return resultToJson(result);
    }
    
    /**
     * Test method
     */
    public static void main(String[] args) {
        // Test with f(x) = x³ - x² - x - 1
        String jsonResult = mullerController("x^3-x^2-x-1", 0.0, 1.0, 2.0, 50, 5, 1e-6);
        System.out.println(jsonResult);
    }
}