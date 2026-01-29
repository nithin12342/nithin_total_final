package com.app.core.algorithms;

import java.util.*;

/**
 * Advanced Algorithm Implementations
 * Demonstrating mastery of computer science fundamentals
 * 
 * This class showcases advanced algorithms with complexity analysis
 * and real-world applications in supply chain optimization
 */
public class AdvancedAlgorithms {

    /**
     * Graph Algorithms for Supply Chain Network Optimization
     */
    public static class GraphAlgorithms {
        
        /**
         * Dijkstra's Algorithm with Priority Queue
         * Time Complexity: O((V + E) log V)
         * Space Complexity: O(V)
         * 
         * Finds shortest path in supply chain network
         */
        public static Map<Integer, Integer> dijkstraShortestPath(
                Map<Integer, List<Edge>> graph, int source) {
            
            Map<Integer, Integer> distances = new HashMap<>();
            PriorityQueue<Node> pq = new PriorityQueue<>(Comparator.comparingInt(n -> n.distance));
            Set<Integer> visited = new HashSet<>();
            
            // Initialize distances
            for (int node : graph.keySet()) {
                distances.put(node, Integer.MAX_VALUE);
            }
            distances.put(source, 0);
            pq.offer(new Node(source, 0));
            
            while (!pq.isEmpty()) {
                Node current = pq.poll();
                if (visited.contains(current.id)) continue;
                
                visited.add(current.id);
                
                for (Edge edge : graph.getOrDefault(current.id, new ArrayList<>())) {
                    int newDistance = current.distance + edge.weight;
                    if (newDistance < distances.get(edge.to)) {
                        distances.put(edge.to, newDistance);
                        pq.offer(new Node(edge.to, newDistance));
                    }
                }
            }
            
            return distances;
        }
        
        /**
         * A* Algorithm for Intelligent Pathfinding
         * Time Complexity: O(b^d) where b is branching factor, d is depth
         * Space Complexity: O(b^d)
         * 
         * Optimized pathfinding with heuristic function
         */
        public static List<Integer> aStarPathfinding(
                Map<Integer, List<Edge>> graph, 
                int start, int goal,
                HeuristicFunction heuristic) {
            
            PriorityQueue<AStarNode> openSet = new PriorityQueue<>(
                Comparator.comparingInt(n -> n.fCost));
            Set<Integer> closedSet = new HashSet<>();
            Map<Integer, Integer> gScore = new HashMap<>();
            Map<Integer, Integer> cameFrom = new HashMap<>();
            
            gScore.put(start, 0);
            openSet.offer(new AStarNode(start, 0, heuristic.calculate(start, goal)));
            
            while (!openSet.isEmpty()) {
                AStarNode current = openSet.poll();
                
                if (current.id == goal) {
                    return reconstructPath(cameFrom, current.id);
                }
                
                closedSet.add(current.id);
                
                for (Edge edge : graph.getOrDefault(current.id, new ArrayList<>())) {
                    if (closedSet.contains(edge.to)) continue;
                    
                    int tentativeGScore = gScore.get(current.id) + edge.weight;
                    
                    if (!gScore.containsKey(edge.to) || tentativeGScore < gScore.get(edge.to)) {
                        cameFrom.put(edge.to, current.id);
                        gScore.put(edge.to, tentativeGScore);
                        int fScore = tentativeGScore + heuristic.calculate(edge.to, goal);
                        openSet.offer(new AStarNode(edge.to, tentativeGScore, fScore));
                    }
                }
            }
            
            return new ArrayList<>(); // No path found
        }
        
        /**
         * Floyd-Warshall Algorithm for All-Pairs Shortest Path
         * Time Complexity: O(V^3)
         * Space Complexity: O(V^2)
         * 
         * Precomputes shortest paths between all pairs of nodes
         */
        public static int[][] floydWarshall(int[][] graph) {
            int V = graph.length;
            int[][] dist = new int[V][V];
            
            // Initialize distance matrix
            for (int i = 0; i < V; i++) {
                for (int j = 0; j < V; j++) {
                    dist[i][j] = graph[i][j];
                }
            }
            
            // Floyd-Warshall algorithm
            for (int k = 0; k < V; k++) {
                for (int i = 0; i < V; i++) {
                    for (int j = 0; j < V; j++) {
                        if (dist[i][k] != Integer.MAX_VALUE && 
                            dist[k][j] != Integer.MAX_VALUE &&
                            dist[i][k] + dist[k][j] < dist[i][j]) {
                            dist[i][j] = dist[i][k] + dist[k][j];
                        }
                    }
                }
            }
            
            return dist;
        }
    }
    
    /**
     * Dynamic Programming Algorithms
     */
    public static class DynamicProgramming {
        
        /**
         * Knapsack Problem with Memoization
         * Time Complexity: O(n * W) where n is items, W is capacity
         * Space Complexity: O(n * W)
         * 
         * Optimizes cargo loading in supply chain
         */
        public static int knapsack01(int[] weights, int[] values, int capacity) {
            int n = weights.length;
            int[][] dp = new int[n + 1][capacity + 1];
            
            for (int i = 1; i <= n; i++) {
                for (int w = 1; w <= capacity; w++) {
                    if (weights[i - 1] <= w) {
                        dp[i][w] = Math.max(
                            values[i - 1] + dp[i - 1][w - weights[i - 1]],
                            dp[i - 1][w]
                        );
                    } else {
                        dp[i][w] = dp[i - 1][w];
                    }
                }
            }
            
            return dp[n][capacity];
        }
        
        /**
         * Longest Common Subsequence
         * Time Complexity: O(m * n)
         * Space Complexity: O(m * n)
         * 
         * Used for sequence matching in logistics
         */
        public static int longestCommonSubsequence(String text1, String text2) {
            int m = text1.length();
            int n = text2.length();
            int[][] dp = new int[m + 1][n + 1];
            
            for (int i = 1; i <= m; i++) {
                for (int j = 1; j <= n; j++) {
                    if (text1.charAt(i - 1) == text2.charAt(j - 1)) {
                        dp[i][j] = dp[i - 1][j - 1] + 1;
                    } else {
                        dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
                    }
                }
            }
            
            return dp[m][n];
        }
        
        /**
         * Edit Distance (Levenshtein Distance)
         * Time Complexity: O(m * n)
         * Space Complexity: O(m * n)
         * 
         * Used for fuzzy string matching in data processing
         */
        public static int editDistance(String word1, String word2) {
            int m = word1.length();
            int n = word2.length();
            int[][] dp = new int[m + 1][n + 1];
            
            // Initialize base cases
            for (int i = 0; i <= m; i++) dp[i][0] = i;
            for (int j = 0; j <= n; j++) dp[0][j] = j;
            
            for (int i = 1; i <= m; i++) {
                for (int j = 1; j <= n; j++) {
                    if (word1.charAt(i - 1) == word2.charAt(j - 1)) {
                        dp[i][j] = dp[i - 1][j - 1];
                    } else {
                        dp[i][j] = 1 + Math.min(
                            Math.min(dp[i - 1][j], dp[i][j - 1]),
                            dp[i - 1][j - 1]
                        );
                    }
                }
            }
            
            return dp[m][n];
        }
    }
    
    /**
     * Greedy Algorithms
     */
    public static class GreedyAlgorithms {
        
        /**
         * Activity Selection Problem
         * Time Complexity: O(n log n)
         * Space Complexity: O(1)
         * 
         * Optimizes resource scheduling in supply chain
         */
        public static List<Activity> activitySelection(List<Activity> activities) {
            // Sort by finish time
            activities.sort(Comparator.comparingInt(a -> a.finish));
            
            List<Activity> selected = new ArrayList<>();
            selected.add(activities.get(0));
            int lastFinishTime = activities.get(0).finish;
            
            for (int i = 1; i < activities.size(); i++) {
                if (activities.get(i).start >= lastFinishTime) {
                    selected.add(activities.get(i));
                    lastFinishTime = activities.get(i).finish;
                }
            }
            
            return selected;
        }
        
        /**
         * Huffman Coding for Data Compression
         * Time Complexity: O(n log n)
         * Space Complexity: O(n)
         * 
         * Optimizes data transmission in IoT networks
         */
        public static Map<Character, String> huffmanCoding(String text) {
            Map<Character, Integer> frequency = new HashMap<>();
            for (char c : text.toCharArray()) {
                frequency.put(c, frequency.getOrDefault(c, 0) + 1);
            }
            
            PriorityQueue<HuffmanNode> pq = new PriorityQueue<>(
                Comparator.comparingInt(n -> n.frequency));
            
            for (Map.Entry<Character, Integer> entry : frequency.entrySet()) {
                pq.offer(new HuffmanNode(entry.getKey(), entry.getValue()));
            }
            
            while (pq.size() > 1) {
                HuffmanNode left = pq.poll();
                HuffmanNode right = pq.poll();
                
                HuffmanNode merged = new HuffmanNode(
                    '\0', left.frequency + right.frequency, left, right);
                pq.offer(merged);
            }
            
            Map<Character, String> codes = new HashMap<>();
            generateCodes(pq.poll(), "", codes);
            return codes;
        }
    }
    
    /**
     * Backtracking Algorithms
     */
    public static class BacktrackingAlgorithms {
        
        /**
         * N-Queens Problem with Pruning
         * Time Complexity: O(N!)
         * Space Complexity: O(N)
         * 
         * Demonstrates constraint satisfaction in optimization
         */
        public static List<List<String>> solveNQueens(int n) {
            List<List<String>> solutions = new ArrayList<>();
            int[] queens = new int[n];
            Arrays.fill(queens, -1);
            
            solveNQueensHelper(queens, 0, solutions);
            return solutions;
        }
        
        private static void solveNQueensHelper(int[] queens, int row, 
                                             List<List<String>> solutions) {
            if (row == queens.length) {
                solutions.add(generateBoard(queens));
                return;
            }
            
            for (int col = 0; col < queens.length; col++) {
                if (isValidPlacement(queens, row, col)) {
                    queens[row] = col;
                    solveNQueensHelper(queens, row + 1, solutions);
                    queens[row] = -1; // Backtrack
                }
            }
        }
        
        /**
         * Sudoku Solver with Constraint Propagation
         * Time Complexity: O(9^(n*n))
         * Space Complexity: O(n*n)
         * 
         * Demonstrates constraint satisfaction and pruning
         */
        public static boolean solveSudoku(int[][] board) {
            for (int i = 0; i < 9; i++) {
                for (int j = 0; j < 9; j++) {
                    if (board[i][j] == 0) {
                        for (int num = 1; num <= 9; num++) {
                            if (isValidSudokuMove(board, i, j, num)) {
                                board[i][j] = num;
                                if (solveSudoku(board)) {
                                    return true;
                                }
                                board[i][j] = 0; // Backtrack
                            }
                        }
                        return false;
                    }
                }
            }
            return true;
        }
    }
    
    /**
     * Network Flow Algorithms
     */
    public static class NetworkFlowAlgorithms {
        
        /**
         * Ford-Fulkerson Algorithm for Maximum Flow
         * Time Complexity: O(E * max_flow)
         * Space Complexity: O(V + E)
         * 
         * Optimizes flow in supply chain networks
         */
        public static int maxFlow(int[][] capacity, int source, int sink) {
            int V = capacity.length;
            int[][] residualCapacity = new int[V][V];
            
            // Initialize residual capacity
            for (int i = 0; i < V; i++) {
                System.arraycopy(capacity[i], 0, residualCapacity[i], 0, V);
            }
            
            int maxFlow = 0;
            int[] parent = new int[V];
            
            while (bfs(residualCapacity, source, sink, parent)) {
                int pathFlow = Integer.MAX_VALUE;
                
                // Find minimum residual capacity along the path
                for (int v = sink; v != source; v = parent[v]) {
                    int u = parent[v];
                    pathFlow = Math.min(pathFlow, residualCapacity[u][v]);
                }
                
                // Update residual capacities
                for (int v = sink; v != source; v = parent[v]) {
                    int u = parent[v];
                    residualCapacity[u][v] -= pathFlow;
                    residualCapacity[v][u] += pathFlow;
                }
                
                maxFlow += pathFlow;
            }
            
            return maxFlow;
        }
        
        /**
         * Minimum Cost Maximum Flow
         * Time Complexity: O(V^2 * E^2)
         * Space Complexity: O(V + E)
         * 
         * Optimizes cost while maximizing flow
         */
        public static int minCostMaxFlow(int[][] capacity, int[][] cost, 
                                       int source, int sink) {
            int V = capacity.length;
            int[][] flow = new int[V][V];
            int totalCost = 0;
            
            while (true) {
                int[] dist = new int[V];
                int[] parent = new int[V];
                Arrays.fill(dist, Integer.MAX_VALUE);
                dist[source] = 0;
                
                // Bellman-Ford algorithm for shortest path
                for (int i = 0; i < V - 1; i++) {
                    for (int u = 0; u < V; u++) {
                        for (int v = 0; v < V; v++) {
                            if (flow[u][v] < capacity[u][v] && 
                                dist[u] != Integer.MAX_VALUE &&
                                dist[u] + cost[u][v] < dist[v]) {
                                dist[v] = dist[u] + cost[u][v];
                                parent[v] = u;
                            }
                        }
                    }
                }
                
                if (dist[sink] == Integer.MAX_VALUE) break;
                
                int pathFlow = Integer.MAX_VALUE;
                for (int v = sink; v != source; v = parent[v]) {
                    int u = parent[v];
                    pathFlow = Math.min(pathFlow, capacity[u][v] - flow[u][v]);
                }
                
                for (int v = sink; v != source; v = parent[v]) {
                    int u = parent[v];
                    flow[u][v] += pathFlow;
                    flow[v][u] -= pathFlow;
                    totalCost += pathFlow * cost[u][v];
                }
            }
            
            return totalCost;
        }
    }
    
    // Helper classes and methods
    static class Edge {
        int to, weight;
        Edge(int to, int weight) {
            this.to = to;
            this.weight = weight;
        }
    }
    
    static class Node {
        int id, distance;
        Node(int id, int distance) {
            this.id = id;
            this.distance = distance;
        }
    }
    
    static class AStarNode {
        int id, gCost, fCost;
        AStarNode(int id, int gCost, int fCost) {
            this.id = id;
            this.gCost = gCost;
            this.fCost = fCost;
        }
    }
    
    static class Activity {
        int start, finish;
        Activity(int start, int finish) {
            this.start = start;
            this.finish = finish;
        }
    }
    
    static class HuffmanNode {
        char character;
        int frequency;
        HuffmanNode left, right;
        
        HuffmanNode(char character, int frequency) {
            this.character = character;
            this.frequency = frequency;
        }
        
        HuffmanNode(char character, int frequency, HuffmanNode left, HuffmanNode right) {
            this.character = character;
            this.frequency = frequency;
            this.left = left;
            this.right = right;
        }
    }
    
    interface HeuristicFunction {
        int calculate(int from, int to);
    }
    
    private static List<Integer> reconstructPath(Map<Integer, Integer> cameFrom, int current) {
        List<Integer> path = new ArrayList<>();
        while (cameFrom.containsKey(current)) {
            path.add(0, current);
            current = cameFrom.get(current);
        }
        path.add(0, current);
        return path;
    }
    
    private static boolean bfs(int[][] residualCapacity, int source, int sink, int[] parent) {
        boolean[] visited = new boolean[residualCapacity.length];
        Queue<Integer> queue = new LinkedList<>();
        queue.offer(source);
        visited[source] = true;
        parent[source] = -1;
        
        while (!queue.isEmpty()) {
            int u = queue.poll();
            for (int v = 0; v < residualCapacity.length; v++) {
                if (!visited[v] && residualCapacity[u][v] > 0) {
                    queue.offer(v);
                    parent[v] = u;
                    visited[v] = true;
                }
            }
        }
        
        return visited[sink];
    }
    
    private static boolean isValidPlacement(int[] queens, int row, int col) {
        for (int i = 0; i < row; i++) {
            if (queens[i] == col || 
                Math.abs(queens[i] - col) == Math.abs(i - row)) {
                return false;
            }
        }
        return true;
    }
    
    private static List<String> generateBoard(int[] queens) {
        List<String> board = new ArrayList<>();
        for (int i = 0; i < queens.length; i++) {
            StringBuilder row = new StringBuilder();
            for (int j = 0; j < queens.length; j++) {
                row.append(queens[i] == j ? 'Q' : '.');
            }
            board.add(row.toString());
        }
        return board;
    }
    
    private static boolean isValidSudokuMove(int[][] board, int row, int col, int num) {
        // Check row
        for (int x = 0; x < 9; x++) {
            if (board[row][x] == num) return false;
        }
        
        // Check column
        for (int x = 0; x < 9; x++) {
            if (board[x][col] == num) return false;
        }
        
        // Check 3x3 box
        int startRow = row - row % 3;
        int startCol = col - col % 3;
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                if (board[i + startRow][j + startCol] == num) return false;
            }
        }
        
        return true;
    }
    
    private static void generateCodes(HuffmanNode root, String code, Map<Character, String> codes) {
        if (root == null) return;
        
        if (root.character != '\0') {
            codes.put(root.character, code);
        }
        
        generateCodes(root.left, code + "0", codes);
        generateCodes(root.right, code + "1", codes);
    }
}
