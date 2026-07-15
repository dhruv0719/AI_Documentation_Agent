// Sample TypeScript module for parser snapshot test
import fs from 'fs';
const lib = require('path');

class Base {}

class MyClass extends Base {
    /** Method doc */
    myMethod(x: number): number {
        return x;
    }

    /** Async method doc */
    async asyncMethod(data: string): Promise<string> {
        return data;
    }

    /** Arrow property doc */
    arrowProp = async (): Promise<void> => {};

    _privateMethod(): void {
        return;
    }
}

// Back-to-back class with no comment - regression check for docstring leak
class NoDocClass extends Base {
    methodNoDoc(): void {
        return;
    }
}

// typed params: required, optional, and default-valued
function greet(name: string, title?: string, punctuation: string = '!') {
    return name;
}

// top-level arrow function with types
const topArrow = (a: number, b: number): number => a + b;

const topAsyncArrow = async (x: number): Promise<number> => x;

function topFunc(x: number): number {
    return x * 2;
}

if (require.main === module) {
    console.log('entry');
}