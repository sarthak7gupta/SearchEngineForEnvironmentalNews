import heapq

h=[(2.5,'a'),(1.5,'b'),(2,'c'),(4,'d')]
heapq.heapify(h)

res=[heapq.heappop(h)]
x=heapq.heappop(h)
while x[0]-res[-1][0] <= 0.5:
  print(h)
  res.append(x)
  x=heapq.heappop(h)

print(res)
