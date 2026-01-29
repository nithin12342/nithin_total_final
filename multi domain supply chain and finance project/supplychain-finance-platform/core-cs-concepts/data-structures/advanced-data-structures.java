package com.app.core.datastructures;

import java.util.*;

/**
 * Advanced Data Structures Implementation
 * Demonstrating mastery of computer science fundamentals
 * 
 * This class showcases custom implementations of advanced data structures
 * with real-world applications in supply chain management
 */
public class AdvancedDataStructures {

    /**
     * B-Tree Implementation for Database Indexing
     * Time Complexity: O(log n) for search, insert, delete
     * Space Complexity: O(n)
     * 
     * Used for efficient database indexing in supply chain data
     */
    public static class BTree<K extends Comparable<K>, V> {
        private static final int DEFAULT_ORDER = 3;
        private final int order;
        private BTreeNode root;
        private int size;

        public BTree() {
            this(DEFAULT_ORDER);
        }

        public BTree(int order) {
            this.order = order;
            this.root = new BTreeNode(true);
        }

        public V get(K key) {
            return get(root, key);
        }

        private V get(BTreeNode node, K key) {
            int i = 0;
            while (i < node.keys.size() && key.compareTo(node.keys.get(i)) > 0) {
                i++;
            }

            if (i < node.keys.size() && key.compareTo(node.keys.get(i)) == 0) {
                return node.values.get(i);
            }

            if (node.isLeaf) {
                return null;
            }

            return get(node.children.get(i), key);
        }

        public void put(K key, V value) {
            if (root.keys.size() == 2 * order - 1) {
                BTreeNode newRoot = new BTreeNode(false);
                newRoot.children.add(root);
                splitChild(newRoot, 0);
                root = newRoot;
            }
            insertNonFull(root, key, value);
            size++;
        }

        private void insertNonFull(BTreeNode node, K key, V value) {
            int i = node.keys.size() - 1;

            if (node.isLeaf) {
                while (i >= 0 && key.compareTo(node.keys.get(i)) < 0) {
                    i--;
                }
                node.keys.add(i + 1, key);
                node.values.add(i + 1, value);
            } else {
                while (i >= 0 && key.compareTo(node.keys.get(i)) < 0) {
                    i--;
                }
                i++;

                if (node.children.get(i).keys.size() == 2 * order - 1) {
                    splitChild(node, i);
                    if (key.compareTo(node.keys.get(i)) > 0) {
                        i++;
                    }
                }

                insertNonFull(node.children.get(i), key, value);
            }
        }

        private void splitChild(BTreeNode parent, int index) {
            BTreeNode child = parent.children.get(index);
            BTreeNode newChild = new BTreeNode(child.isLeaf);

            // Move keys and values
            for (int i = 0; i < order - 1; i++) {
                newChild.keys.add(child.keys.remove(order));
                newChild.values.add(child.values.remove(order));
            }

            if (!child.isLeaf) {
                for (int i = 0; i < order; i++) {
                    newChild.children.add(child.children.remove(order));
                }
            }

            parent.children.add(index + 1, newChild);
            parent.keys.add(index, child.keys.remove(order - 1));
            parent.values.add(index, child.values.remove(order - 1));
        }

        private static class BTreeNode {
            List<Comparable> keys;
            List<Object> values;
            List<BTreeNode> children;
            boolean isLeaf;

            BTreeNode(boolean isLeaf) {
                this.isLeaf = isLeaf;
                this.keys = new ArrayList<>();
                this.values = new ArrayList<>();
                this.children = new ArrayList<>();
            }
        }
    }

    /**
     * Skip List Implementation for Fast Searching
     * Time Complexity: O(log n) average case
     * Space Complexity: O(n)
     * 
     * Used for fast searching in large datasets
     */
    public static class SkipList<T extends Comparable<T>> {
        private static final double PROBABILITY = 0.5;
        private SkipListNode head;
        private int size;
        private Random random;

        public SkipList() {
            this.head = new SkipListNode(null, 0);
            this.size = 0;
            this.random = new Random();
        }

        public boolean contains(T value) {
            SkipListNode current = head;
            for (int level = head.level; level >= 0; level--) {
                while (current.forward[level] != null && 
                       current.forward[level].value.compareTo(value) < 0) {
                    current = current.forward[level];
                }
            }
            current = current.forward[0];
            return current != null && current.value.equals(value);
        }

        public void insert(T value) {
            SkipListNode[] update = new SkipListNode[head.level + 1];
            SkipListNode current = head;

            for (int level = head.level; level >= 0; level--) {
                while (current.forward[level] != null && 
                       current.forward[level].value.compareTo(value) < 0) {
                    current = current.forward[level];
                }
                update[level] = current;
            }

            current = current.forward[0];

            if (current == null || !current.value.equals(value)) {
                int newLevel = randomLevel();
                if (newLevel > head.level) {
                    update = Arrays.copyOf(update, newLevel + 1);
                    for (int i = head.level + 1; i <= newLevel; i++) {
                        update[i] = head;
                    }
                    head.level = newLevel;
                }

                SkipListNode newNode = new SkipListNode(value, newLevel);
                for (int i = 0; i <= newLevel; i++) {
                    newNode.forward[i] = update[i].forward[i];
                    update[i].forward[i] = newNode;
                }
                size++;
            }
        }

        public void delete(T value) {
            SkipListNode[] update = new SkipListNode[head.level + 1];
            SkipListNode current = head;

            for (int level = head.level; level >= 0; level--) {
                while (current.forward[level] != null && 
                       current.forward[level].value.compareTo(value) < 0) {
                    current = current.forward[level];
                }
                update[level] = current;
            }

            current = current.forward[0];

            if (current != null && current.value.equals(value)) {
                for (int i = 0; i <= head.level; i++) {
                    if (update[i].forward[i] != current) {
                        break;
                    }
                    update[i].forward[i] = current.forward[i];
                }

                while (head.level > 0 && head.forward[head.level] == null) {
                    head.level--;
                }
                size--;
            }
        }

        private int randomLevel() {
            int level = 0;
            while (random.nextDouble() < PROBABILITY && level < 16) {
                level++;
            }
            return level;
        }

        private static class SkipListNode {
            Comparable value;
            SkipListNode[] forward;
            int level;

            SkipListNode(Comparable value, int level) {
                this.value = value;
                this.level = level;
                this.forward = new SkipListNode[level + 1];
            }
        }
    }

    /**
     * Trie (Prefix Tree) Implementation
     * Time Complexity: O(m) where m is length of string
     * Space Complexity: O(ALPHABET_SIZE * N * M)
     * 
     * Used for efficient string matching in product catalogs
     */
    public static class Trie {
        private TrieNode root;

        public Trie() {
            this.root = new TrieNode();
        }

        public void insert(String word) {
            TrieNode current = root;
            for (char c : word.toCharArray()) {
                if (!current.children.containsKey(c)) {
                    current.children.put(c, new TrieNode());
                }
                current = current.children.get(c);
            }
            current.isEndOfWord = true;
        }

        public boolean search(String word) {
            TrieNode current = root;
            for (char c : word.toCharArray()) {
                if (!current.children.containsKey(c)) {
                    return false;
                }
                current = current.children.get(c);
            }
            return current.isEndOfWord;
        }

        public boolean startsWith(String prefix) {
            TrieNode current = root;
            for (char c : prefix.toCharArray()) {
                if (!current.children.containsKey(c)) {
                    return false;
                }
                current = current.children.get(c);
            }
            return true;
        }

        public List<String> getAllWordsWithPrefix(String prefix) {
            List<String> words = new ArrayList<>();
            TrieNode current = root;
            
            // Navigate to prefix
            for (char c : prefix.toCharArray()) {
                if (!current.children.containsKey(c)) {
                    return words;
                }
                current = current.children.get(c);
            }
            
            // Collect all words from this node
            collectWords(current, prefix, words);
            return words;
        }

        private void collectWords(TrieNode node, String prefix, List<String> words) {
            if (node.isEndOfWord) {
                words.add(prefix);
            }
            
            for (Map.Entry<Character, TrieNode> entry : node.children.entrySet()) {
                collectWords(entry.getValue(), prefix + entry.getKey(), words);
            }
        }

        private static class TrieNode {
            Map<Character, TrieNode> children;
            boolean isEndOfWord;

            TrieNode() {
                this.children = new HashMap<>();
                this.isEndOfWord = false;
            }
        }
    }

    /**
     * Segment Tree Implementation for Range Queries
     * Time Complexity: O(log n) for query and update
     * Space Complexity: O(n)
     * 
     * Used for efficient range queries in time-series data
     */
    public static class SegmentTree {
        private int[] tree;
        private int[] data;
        private int n;

        public SegmentTree(int[] arr) {
            this.data = arr.clone();
            this.n = arr.length;
            this.tree = new int[4 * n];
            build(1, 0, n - 1);
        }

        private void build(int node, int start, int end) {
            if (start == end) {
                tree[node] = data[start];
            } else {
                int mid = (start + end) / 2;
                build(2 * node, start, mid);
                build(2 * node + 1, mid + 1, end);
                tree[node] = tree[2 * node] + tree[2 * node + 1];
            }
        }

        public void update(int index, int value) {
            update(1, 0, n - 1, index, value);
        }

        private void update(int node, int start, int end, int index, int value) {
            if (start == end) {
                data[index] = value;
                tree[node] = value;
            } else {
                int mid = (start + end) / 2;
                if (index <= mid) {
                    update(2 * node, start, mid, index, value);
                } else {
                    update(2 * node + 1, mid + 1, end, index, value);
                }
                tree[node] = tree[2 * node] + tree[2 * node + 1];
            }
        }

        public int query(int left, int right) {
            return query(1, 0, n - 1, left, right);
        }

        private int query(int node, int start, int end, int left, int right) {
            if (right < start || left > end) {
                return 0;
            }
            if (left <= start && end <= right) {
                return tree[node];
            }
            int mid = (start + end) / 2;
            int leftSum = query(2 * node, start, mid, left, right);
            int rightSum = query(2 * node + 1, mid + 1, end, left, right);
            return leftSum + rightSum;
        }
    }

    /**
     * Disjoint Set Union (Union-Find) Implementation
     * Time Complexity: O(α(n)) amortized where α is inverse Ackermann function
     * Space Complexity: O(n)
     * 
     * Used for cycle detection and connected components
     */
    public static class DisjointSetUnion {
        private int[] parent;
        private int[] rank;
        private int components;

        public DisjointSetUnion(int n) {
            this.parent = new int[n];
            this.rank = new int[n];
            this.components = n;
            
            for (int i = 0; i < n; i++) {
                parent[i] = i;
                rank[i] = 0;
            }
        }

        public int find(int x) {
            if (parent[x] != x) {
                parent[x] = find(parent[x]); // Path compression
            }
            return parent[x];
        }

        public boolean union(int x, int y) {
            int rootX = find(x);
            int rootY = find(y);

            if (rootX == rootY) {
                return false; // Already in same set
            }

            // Union by rank
            if (rank[rootX] < rank[rootY]) {
                parent[rootX] = rootY;
            } else if (rank[rootX] > rank[rootY]) {
                parent[rootY] = rootX;
            } else {
                parent[rootY] = rootX;
                rank[rootX]++;
            }

            components--;
            return true;
        }

        public boolean connected(int x, int y) {
            return find(x) == find(y);
        }

        public int getComponentCount() {
            return components;
        }
    }

    /**
     * Fenwick Tree (Binary Indexed Tree) Implementation
     * Time Complexity: O(log n) for query and update
     * Space Complexity: O(n)
     * 
     * Used for efficient prefix sum queries
     */
    public static class FenwickTree {
        private int[] tree;
        private int n;

        public FenwickTree(int size) {
            this.n = size;
            this.tree = new int[n + 1];
        }

        public void update(int index, int delta) {
            index++; // 1-indexed
            while (index <= n) {
                tree[index] += delta;
                index += index & (-index); // Add least significant bit
            }
        }

        public int query(int index) {
            index++; // 1-indexed
            int sum = 0;
            while (index > 0) {
                sum += tree[index];
                index -= index & (-index); // Remove least significant bit
            }
            return sum;
        }

        public int rangeQuery(int left, int right) {
            return query(right) - query(left - 1);
        }
    }

    /**
     * LRU Cache Implementation
     * Time Complexity: O(1) for get and put
     * Space Complexity: O(capacity)
     * 
     * Used for caching frequently accessed data
     */
    public static class LRUCache<K, V> {
        private final int capacity;
        private final Map<K, Node<K, V>> cache;
        private final Node<K, V> head;
        private final Node<K, V> tail;

        public LRUCache(int capacity) {
            this.capacity = capacity;
            this.cache = new HashMap<>();
            this.head = new Node<>(null, null);
            this.tail = new Node<>(null, null);
            head.next = tail;
            tail.prev = head;
        }

        public V get(K key) {
            Node<K, V> node = cache.get(key);
            if (node == null) {
                return null;
            }
            moveToHead(node);
            return node.value;
        }

        public void put(K key, V value) {
            Node<K, V> node = cache.get(key);
            
            if (node != null) {
                node.value = value;
                moveToHead(node);
            } else {
                Node<K, V> newNode = new Node<>(key, value);
                
                if (cache.size() >= capacity) {
                    Node<K, V> tail = removeTail();
                    cache.remove(tail.key);
                }
                
                cache.put(key, newNode);
                addToHead(newNode);
            }
        }

        private void addToHead(Node<K, V> node) {
            node.prev = head;
            node.next = head.next;
            head.next.prev = node;
            head.next = node;
        }

        private void removeNode(Node<K, V> node) {
            node.prev.next = node.next;
            node.next.prev = node.prev;
        }

        private void moveToHead(Node<K, V> node) {
            removeNode(node);
            addToHead(node);
        }

        private Node<K, V> removeTail() {
            Node<K, V> lastNode = tail.prev;
            removeNode(lastNode);
            return lastNode;
        }

        private static class Node<K, V> {
            K key;
            V value;
            Node<K, V> prev;
            Node<K, V> next;

            Node(K key, V value) {
                this.key = key;
                this.value = value;
            }
        }
    }

    /**
     * Circular Buffer Implementation
     * Time Complexity: O(1) for enqueue and dequeue
     * Space Complexity: O(capacity)
     * 
     * Used for efficient data streaming and buffering
     */
    public static class CircularBuffer<T> {
        private final T[] buffer;
        private final int capacity;
        private int head;
        private int tail;
        private int size;

        @SuppressWarnings("unchecked")
        public CircularBuffer(int capacity) {
            this.capacity = capacity;
            this.buffer = (T[]) new Object[capacity];
            this.head = 0;
            this.tail = 0;
            this.size = 0;
        }

        public boolean enqueue(T item) {
            if (isFull()) {
                return false;
            }
            
            buffer[tail] = item;
            tail = (tail + 1) % capacity;
            size++;
            return true;
        }

        public T dequeue() {
            if (isEmpty()) {
                return null;
            }
            
            T item = buffer[head];
            buffer[head] = null;
            head = (head + 1) % capacity;
            size--;
            return item;
        }

        public T peek() {
            if (isEmpty()) {
                return null;
            }
            return buffer[head];
        }

        public boolean isEmpty() {
            return size == 0;
        }

        public boolean isFull() {
            return size == capacity;
        }

        public int size() {
            return size;
        }

        public void clear() {
            Arrays.fill(buffer, null);
            head = 0;
            tail = 0;
            size = 0;
        }
    }
}
