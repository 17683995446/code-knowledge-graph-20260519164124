// 复杂的JavaScript项目测试

// 泛型和接口模拟
class GenericRepository<T> {
  constructor(private items: T[] = []) {}

  add(item: T): void {
    this.items.push(item);
  }

  getAll(): T[] {
    return [...this.items];
  }

  find(predicate: (item: T) => boolean): T | undefined {
    return this.items.find(predicate);
  }
}

// 装饰器模式实现
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  descriptor.value = function(...args: any[]) {
    console.log(`Calling ${propertyKey} with`, args);
    return originalMethod.apply(this, args);
  };
  return descriptor;
}

class UserService {
  private users: Map<string, User> = new Map();

  @log
  createUser(name: string, email: string): User {
    const id = crypto.randomUUID();
    const user = new User(id, name, email);
    this.users.set(id, user);
    return user;
  }

  getUser(id: string): User | undefined {
    return this.users.get(id);
  }

  getAllUsers(): User[] {
    return Array.from(this.users.values());
  }
}

// 接口定义
interface ISerializable {
  serialize(): string;
  deserialize(data: string): void;
}

interface IValidatable {
  validate(): boolean;
  getValidationErrors(): string[];
}

// 模型类
class User implements ISerializable, IValidatable {
  private _validationErrors: string[] = [];

  constructor(
    public id: string,
    public name: string,
    public email: string,
    public age?: number
  ) {}

  serialize(): string {
    return JSON.stringify({
      id: this.id,
      name: this.name,
      email: this.email,
      age: this.age
    });
  }

  deserialize(data: string): void {
    const obj = JSON.parse(data);
    this.id = obj.id;
    this.name = obj.name;
    this.email = obj.email;
    this.age = obj.age;
  }

  validate(): boolean {
    this._validationErrors = [];
    
    if (!this.name || this.name.trim().length === 0) {
      this._validationErrors.push('Name is required');
    }
    
    if (!this.email || !this.email.includes('@')) {
      this._validationErrors.push('Invalid email format');
    }
    
    if (this.age !== undefined && (this.age < 0 || this.age > 150)) {
      this._validationErrors.push('Invalid age');
    }
    
    return this._validationErrors.length === 0;
  }

  getValidationErrors(): string[] {
    return this._validationErrors;
  }
}

// 抽象类
abstract class BaseProcessor<T> {
  protected items: T[] = [];

  abstract process(item: T): T;

  add(item: T): void {
    this.items.push(item);
  }

  getAll(): T[] {
    return [...this.items];
  }
}

// 具体处理器
class StringProcessor extends BaseProcessor<string> {
  process(item: string): string {
    return item.trim().toUpperCase();
  }
}

class NumberProcessor extends BaseProcessor<number> {
  process(item: number): number {
    return item * 2;
  }
}

// Mixin 实现
const Timestamped = <T extends new(...args: any[]) => {}>(Base: T) => {
  return class extends Base {
    createdAt: Date = new Date();
    updatedAt: Date = new Date();

    touch() {
      this.updatedAt = new Date();
    }
  };
};

class TimestampedUser extends Timestamped(User) {
  // 扩展时间戳功能
}

// 观察者模式
interface Observer {
  update(data: any): void;
}

interface Subject {
  attach(observer: Observer): void;
  detach(observer: Observer): void;
  notify(): void;
}

class EventEmitter implements Subject {
  private observers: Observer[] = [];
  private data: any;

  attach(observer: Observer): void {
    this.observers.push(observer);
  }

  detach(observer: Observer): void {
    this.observers = this.observers.filter(o => o !== observer);
  }

  notify(): void {
    this.observers.forEach(o => o.update(this.data));
  }

  emit(data: any): void {
    this.data = data;
    this.notify();
  }
}

// 工厂模式
class Animal {
  constructor(public name: string) {}
  speak(): string {
    return `${this.name} makes a sound`;
  }
}

class Dog extends Animal {
  speak(): string {
    return `${this.name} barks`;
  }
}

class Cat extends Animal {
  speak(): string {
    return `${this.name} meows`;
  }
}

class AnimalFactory {
  static createAnimal(type: 'dog' | 'cat', name: string): Animal {
    switch (type) {
      case 'dog':
        return new Dog(name);
      case 'cat':
        return new Cat(name);
      default:
        throw new Error(`Unknown animal type: ${type}`);
    }
  }
}

// Promise 和 async/await
class AsyncDataService {
  private cache: Map<string, any> = new Map();

  async fetchData<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
    if (this.cache.has(key)) {
      return this.cache.get(key);
    }

    const data = await fetcher();
    this.cache.set(key, data);
    return data;
  }

  async fetchWithRetry<T>(
    fetcher: () => Promise<T>,
    retries: number = 3
  ): Promise<T> {
    for (let i = 0; i < retries; i++) {
      try {
        return await fetcher();
      } catch (error) {
        if (i === retries - 1) throw error;
        await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
      }
    }
    throw new Error('Max retries exceeded');
  }
}

// 函数式编程工具
const pipe = (...fns: Function[]) => (x: any) =>
  fns.reduce((v, f) => f(v), x);

const compose = (...fns: Function[]) => (x: any) =>
  fns.reduceRight((v, f) => f(v), x);

const curry = (fn: Function) => {
  return function curried(...args: any[]) {
    if (args.length >= fn.length) {
      return fn.apply(this, args);
    }
    return (...nextArgs: any[]) => curried(...args, ...nextArgs);
  };
};

// 闭包和模块模式
const createCounter = (() => {
  let count = 0;
  return {
    increment: () => ++count,
    decrement: () => --count,
    getCount: () => count,
    reset: () => {
      count = 0;
    }
  };
})();

// 生成器
function* idGenerator() {
  let id = 1;
  while (true) {
    yield id++;
  }
}

const idGen = idGenerator();

// Symbol 和迭代器
class Collection<T> implements Iterable<T> {
  private items: T[] = [];

  add(item: T): void {
    this.items.push(item);
  }

  *[Symbol.iterator](): Iterator<T> {
    for (const item of this.items) {
      yield item;
    }
  }
}

// Proxy 和 Reflect
const validatorProxy = new Proxy({}, {
  set(target: any, property: string, value: any) {
    if (property === 'age' && (value < 0 || value > 150)) {
      throw new Error('Invalid age');
    }
    Reflect.set(target, property, value);
    return true;
  }
});

// Web API 模拟
interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

class APIManager {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<APIResponse<T>> {
    try {
      // 模拟请求
      const response = await fetch(`${this.baseURL}${endpoint}`, options);
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return { success: false, error: String(error) };
    }
  }

  async get<T>(endpoint: string): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, body: any): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
  }
}

// 导出
export {
  UserService,
  User,
  GenericRepository,
  AnimalFactory,
  Animal,
  EventEmitter,
  AsyncDataService,
  Collection,
  pipe,
  compose,
  curry,
  createCounter
};
