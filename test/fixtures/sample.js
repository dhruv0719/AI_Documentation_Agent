// Sample JavaScript module for parser snapshot test
import fs from 'fs';
const lib = require('path');

class Base {}

class MyClass extends Base {
    /** Method doc */
    myMethod(x) {
        return x;
    }

    /** Async method doc */
    async asyncMethod(data) {
        return data;
    }

    /** Arrow property doc */
    arrowProp = async () => {};

    _privateMethod() {
        return null;
    }
}

// Back-to-back class with no comment - regression check for docstring leak
class NoDocClass extends Base {
    methodNoDoc() {
        return null;
    }
}

// top-level arrow function
const topArrow = (a, b) => a + b;

// top-level async arrow function
const topAsyncArrow = async (x) => x;

function topFunc(x) {
    return x * 2;
}

function _privateTopFunc() {
    return null;
}

if (require.main === module) {
    console.log('entry');
}