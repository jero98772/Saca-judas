let calculatorImg;
let pressedKeys = [];
let calculators = [];
const keyPositions = [
    { x: 30, y: 110, w: 40, h: 30, key: '7' },
    { x: 80, y: 110, w: 40, h: 30, key: '8' },
    { x: 130, y: 110, w: 40, h: 30, key: '9' },
    { x: 30, y: 150, w: 40, h: 30, key: '4' },
    { x: 80, y: 150, w: 40, h: 30, key: '5' },
    { x: 130, y: 150, w: 40, h: 30, key: '6' },
    { x: 30, y: 190, w: 40, h: 30, key: '1' },
    { x: 80, y: 190, w: 40, h: 30, key: '2' },
    { x: 130, y: 190, w: 40, h: 30, key: '3' },
    { x: 30, y: 230, w: 40, h: 30, key: '0' },
    { x: 80, y: 230, w: 40, h: 30, key: '.' },
    { x: 130, y: 230, w: 40, h: 30, key: '=' },
    { x: 180, y: 110, w: 40, h: 30, key: '/' },
    { x: 180, y: 150, w: 40, h: 30, key: '*' },
    { x: 180, y: 190, w: 40, h: 30, key: '-' },
    { x: 180, y: 230, w: 40, h: 30, key: '+' }
];

function preload() {
    calculatorImg = loadImage('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="250" height="300" viewBox="0 0 250 300"><rect x="10" y="10" width="230" height="280" rx="10" fill="%23222" stroke="%2300cc44" stroke-width="2"/><rect x="20" y="40" width="210" height="50" rx="5" fill="%23003311" stroke="%2300cc44" stroke-width="1"/><text x="30" y="75" font-family="monospace" font-size="20" fill="%2300ff66">0</text></svg>');
}

function setup() {
    createCanvas(windowWidth, windowHeight);
    textFont('Courier New');
    textSize(16);
    
    // Create multiple calculator instances
    for (let i = 0; i < 15; i++) {
        calculators.push(new Calculator());
    }
    
    // Optional: Try to set up button interaction if button exists
    // This won't break if the button doesn't exist
    const button = document.getElementById('calculation-btn');
    if (button) {
        button.addEventListener('click', () => {
            createButtonEffect();
            intensifyAnimations();
        });
    }
    
    // Alternative: Add mouse click interaction for creating effects
    // This works regardless of button presence
    document.addEventListener('click', (e) => {
        // Only trigger if clicking on the canvas area, not on buttons
        if (e.target.tagName !== 'BUTTON' && e.target.tagName !== 'A') {
            createButtonEffect();
            intensifyAnimations();
        }
    });
}

function draw() {
    clear();
    background(15, 15, 35, 200);
    
    // Draw all calculator instances
    calculators.forEach(calc => {
        calc.update();
        calc.display();
    });
    
    // Draw pressed keys effects
    for (let i = pressedKeys.length - 1; i >= 0; i--) {
        pressedKeys[i].update();
        pressedKeys[i].display();
        if (pressedKeys[i].alpha <= 0) {
            pressedKeys.splice(i, 1);
        }
    }
}

class Calculator {
    constructor() {
        this.x = random(width);
        this.y = random(height);
        this.size = random(0.8, 1.2);
        this.speed = random(0.5, 2);
        this.angle = random(TWO_PI);
        this.keys = [];
        this.lastPress = 0;
        
        // Create key states
        keyPositions.forEach(pos => {
            this.keys.push({
                ...pos,
                pressed: false,
                pressTime: 0
            });
        });
    }
    
    update() {
        // Move calculator
        this.x += cos(this.angle) * this.speed;
        this.y += sin(this.angle) * this.speed;
        
        // Bounce off edges
        if (this.x < 0 || this.x > width) this.angle = PI - this.angle;
        if (this.y < 0 || this.y > height) this.angle = -this.angle;
        
        // Keep calculators within bounds
        this.x = constrain(this.x, 0, width);
        this.y = constrain(this.y, 0, height);
        
        // Random key presses
        if (millis() - this.lastPress > random(200, 1000)) {
            const keyIndex = floor(random(this.keys.length));
            this.keys[keyIndex].pressed = true;
            this.keys[keyIndex].pressTime = millis();
            
            // Add visual effect
            const key = this.keys[keyIndex];
            pressedKeys.push(new KeyEffect(
                this.x + key.x * this.size,
                this.y + key.y * this.size,
                key.w * this.size,
                key.h * this.size,
                key.key
            ));
            
            this.lastPress = millis();
        }
        
        // Reset key press after delay
        this.keys.forEach(key => {
            if (key.pressed && millis() - key.pressTime > 200) {
                key.pressed = false;
            }
        });
    }
    
    display() {
        push();
        translate(this.x, this.y);
        scale(this.size);
        
        // Draw calculator body
        image(calculatorImg, 0, 0);
        
        // Draw keys
        fill(30);
        stroke(0, 200, 100);
        strokeWeight(1);
        
        this.keys.forEach(key => {
            if (key.pressed) {
                fill(0, 100, 40);
            } else {
                fill(30);
            }
            
            rect(key.x, key.y, key.w, key.h, 3);
            fill(0, 200, 100);
            noStroke();
            textAlign(CENTER, CENTER);
            text(key.key, key.x + key.w/2, key.y + key.h/2);
        });
        
        pop();
    }
}

class KeyEffect {
    constructor(x, y, w, h, key) {
        this.x = x;
        this.y = y;
        this.w = w;
        this.h = h;
        this.key = key;
        this.alpha = 255;
        this.size = 1;
    }
    
    update() {
        this.alpha -= 5;
        this.size += 0.02;
    }
    
    display() {
        push();
        translate(this.x + this.w/2, this.y + this.h/2);
        scale(this.size);
        noFill();
        stroke(0, 255, 100, this.alpha);
        strokeWeight(2);
        rect(-this.w/2, -this.h/2, this.w, this.h, 3);
        
        fill(0, 255, 100, this.alpha * 0.7);
        noStroke();
        textAlign(CENTER, CENTER);
        text(this.key, 0, 0);
        pop();
    }
}

function createButtonEffect() {
    for (let i = 0; i < 10; i++) {
        setTimeout(() => {
            const randomKey = random(keyPositions);
            pressedKeys.push(new KeyEffect(
                random(width),
                random(height),
                randomKey.w,
                randomKey.h,
                randomKey.key
            ));
        }, i * 100);
    }
}

function intensifyAnimations() {
    calculators.forEach(calc => {
        calc.speed *= 2;
        setTimeout(() => {
            calc.speed /= 2;
        }, 3000);
    });
}

// Handle window resize
function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
}

// Optional: Add keyboard interaction for extra effects
function keyPressed() {
    if (key === ' ') { // Spacebar
        createButtonEffect();
        intensifyAnimations();
    }
}