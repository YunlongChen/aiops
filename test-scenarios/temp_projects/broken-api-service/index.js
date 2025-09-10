
// Injected runtime error: memory_leak
const memoryLeak = []; setInterval(() => { memoryLeak.push(new Array(1000000)); }, 100);
