// 复杂Go项目测试

package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// 泛型结构体 (Go 1.18+)
type Stack[T any] struct {
	items []T
	mu    sync.Mutex
}

func (s *Stack[T]) Push(item T) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.items = append(s.items, item)
}

func (s *Stack[T]) Pop() (T, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if len(s.items) == 0 {
		var zero T
		return zero, false
	}
	item := s.items[len(s.items)-1]
	s.items = s.items[:len(s.items)-1]
	return item, true
}

// 接口定义
type Repository interface {
	Create(ctx context.Context, entity interface{}) error
	GetByID(ctx context.Context, id string) (interface{}, error)
	Update(ctx context.Context, entity interface{}) error
	Delete(ctx context.Context, id string) error
}

type Cache interface {
	Set(key string, value interface{}) error
	Get(key string) (interface{}, error)
	Delete(key string) error
}

// 结构体嵌套
type User struct {
	ID        string    `json:"id"`
	Name      string    `json:"name"`
	Email     string    `json:"email"`
	Profile   UserProfile
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type UserProfile struct {
	Bio      string   `json:"bio"`
	Avatar   string   `json:"avatar"`
	Interests []string `json:"interests"`
}

// 方法接收器
func (u *User) Validate() bool {
	if u.Name == "" || u.Email == "" {
		return false
	}
	if len(u.Profile.Interests) > 10 {
		return false
	}
	return true
}

func (u *User) ToString() string {
	return fmt.Sprintf("User{ID:%s, Name:%s, Email:%s}", u.ID, u.Name, u.Email)
}

// 结构体方法
type Order struct {
	ID        string
	UserID    string
	Items     []OrderItem
	Total     float64
	Status    OrderStatus
	CreatedAt time.Time
}

type OrderItem struct {
	ProductID string
	Name      string
	Quantity  int
	Price     float64
}

type OrderStatus int

const (
	StatusPending OrderStatus = iota
	StatusProcessing
	StatusCompleted
	StatusCancelled
)

func (s OrderStatus) String() string {
	switch s {
	case StatusPending:
		return "pending"
	case StatusProcessing:
		return "processing"
	case StatusCompleted:
		return "completed"
	case StatusCancelled:
		return "cancelled"
	default:
		return "unknown"
	}
}

// 接口组合
type ReadRepository interface {
	GetByID(ctx context.Context, id string) (interface{}, error)
	GetAll(ctx context.Context) ([]interface{}, error)
}

type WriteRepository interface {
	Create(ctx context.Context, entity interface{}) error
	Update(ctx context.Context, entity interface{}) error
	Delete(ctx context.Context, id string) error
}

type CRUDRepository interface {
	ReadRepository
	WriteRepository
}

// 工厂模式
type Logger interface {
	Log(message string)
}

type ConsoleLogger struct{}

func (l *ConsoleLogger) Log(message string) {
	fmt.Println("[LOG]", message)
}

type FileLogger struct {
	filename string
}

func (l *FileLogger) Log(message string) {
	fmt.Printf("[FILE:%s] %s\n", l.filename, message)
}

type LoggerFactory struct{}

func (f *LoggerFactory) CreateLogger(loggerType string) Logger {
	switch loggerType {
	case "console":
		return &ConsoleLogger{}
	case "file":
		return &FileLogger{filename: "app.log"}
	default:
		return &ConsoleLogger{}
	}
}

// 观察者模式
type Observer interface {
	Update(event string, data interface{})
}

type Subject struct {
	observers []Observer
	mu        sync.RWMutex
}

func (s *Subject) Attach(o Observer) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.observers = append(s.observers, o)
}

func (s *Subject) Detach(o Observer) {
	s.mu.Lock()
	defer s.mu.Unlock()
	for i, obs := range s.observers {
		if obs == o {
			s.observers = append(s.observers[:i], s.observers[i+1:]...)
			break
		}
	}
}

func (s *Subject) Notify(event string, data interface{}) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	for _, o := range s.observers {
		o.Update(event, data)
	}
}

// Channel 和 Goroutine
type WorkerPool struct {
	workers   int
	taskChan chan func()
	wg       sync.WaitGroup
}

func NewWorkerPool(workers int) *WorkerPool {
	pool := &WorkerPool{
		workers:   workers,
		taskChan: make(chan func(), 100),
	}
	pool.start()
	return pool
}

func (p *WorkerPool) start() {
	for i := 0; i < p.workers; i++ {
		p.wg.Add(1)
		go func() {
			defer p.wg.Done()
			for task := range p.taskChan {
				task()
			}
		}()
	}
}

func (p *WorkerPool) Submit(task func()) {
	p.taskChan <- task
}

func (p *WorkerPool) Shutdown() {
	close(p.taskChan)
	p.wg.Wait()
}

// Context 使用
type Service struct {
	name string
}

func (s *Service) DoSomething(ctx context.Context) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	case <-time.After(time.Second):
		fmt.Printf("Service %s completed\n", s.name)
		return nil
	}
}

// 错误处理
type ApplicationError struct {
	Code    int
	Message string
	Err     error
}

func (e *ApplicationError) Error() string {
	return fmt.Sprintf("Error %d: %s", e.Code, e.Message)
}

func (e *ApplicationError) Unwrap() error {
	return e.Err
}

// 装饰器模式
type Middleware func(http.Handler) http.Handler

func LoggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		fmt.Printf("Request: %s %s\n", r.Method, r.URL.Path)
		next.ServeHTTP(w, r)
	})
}

// HTTP Handler (需要 net/http)
type Handler struct{}

func (h *Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello, World!")
}

// 函数式编程
type Transform func(int) int

func Pipeline(Transforms ...Transform) Transform {
	return func(n int) int {
		result := n
		for _, t := range Transforms {
			result = t(result)
		}
		return result
	}
}

// defer 和 panic/recover
func SafeCall(fn func()) (err error) {
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("panic recovered: %v", r)
		}
	}()
	fn()
	return nil
}

// 泛型接口
type Comparable interface {
	Less(other interface{}) bool
}

type Person struct {
	Name string
	Age  int
}

func (p Person) Less(other interface{}) bool {
	o := other.(Person)
	return p.Age < o.Age
}

// Map 和 Slice 操作
type Cache[K comparable, V any] struct {
	data map[K]V
	mu   sync.RWMutex
}

func NewCache[K comparable, V any]() *Cache[K, V] {
	return &Cache[K, V]{
		data: make(map[K]V),
	}
}

func (c *Cache[K, V]) Set(key K, value V) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.data[key] = value
}

func (c *Cache[K, V]) Get(key K) (V, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	value, ok := c.data[key]
	return value, ok
}

// 测试用 main 函数
func main() {
	// 泛型栈测试
	intStack := &Stack[int]{}
	intStack.Push(1)
	intStack.Push(2)
	val, _ := intStack.Pop()
	fmt.Printf("Popped: %d\n", val)

	// 用户测试
	user := &User{
		ID:    "123",
		Name:  "John",
		Email: "john@example.com",
		Profile: UserProfile{
			Bio:       "Developer",
			Interests: []string{"coding", "reading"},
		},
	}
	fmt.Println(user.ToString())

	// 工厂模式测试
	factory := &LoggerFactory{}
	logger := factory.CreateLogger("console")
	logger.Log("Hello, World!")

	// 工作者池测试
	pool := NewWorkerPool(3)
	pool.Submit(func() {
		fmt.Println("Task 1")
	})
	pool.Submit(func() {
		fmt.Println("Task 2")
	})
	pool.Shutdown()

	// 缓存测试
	cache := NewCache[string, int]()
	cache.Set("key1", 100)
	val, ok := cache.Get("key1")
	if ok {
		fmt.Printf("Cache value: %d\n", val)
	}
}
