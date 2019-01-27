# CSC8101 2018-19 Coursework assignment

This is about building models for providing movie recommendations. 
We use the ALS algorithm (see lecture notes) with explicit movie ratings.
We use the entire movielens dataset. 

However, building the model out of the dataset is only one of the tasks. 
Please refer to the figure below.

We note that we can create a user-user network from the user-movie-ratings (U-M-R) matrix, i.e., where each user is represented by a node, and there is an edge between two users u1, u2 if u1 and u2 have rated the same movie. The *weight* of the edge is the number of the same movies that have both rated. Note that for simplicity here we ignore the values of the ratings. 
Once we have the network, it makes sense to partition it into communities of users, so that users who have rated many of the same movies will likely belong to the same community.

At this point, we build one recommender model using the same ALS approach, but *separately for each community*.
The exercise ends with a comparison of the performance of the global model relative to the smaller community models. 
is it true that the models that only consider users within a community perform better for that community than the global model?

![assignment tasks summary](resources/Coursework-tasks.png)

All programming is in Python for Spark and occurs using Databricks notebooks, attached to the shared Spark cluster provided for the module.

Details of each of the tasks are given below.

## The MovieLens dataset
The original datasets are [here](https://grouplens.org/datasets/movielens/).

The dataset comes in two sizes:
- small, for code debugging purposes. Download and inspect from [here](data/ml-latest-small.zip).
   this contains 100,000 ratings applied to 9,000 movies by 600 users. Last updated 9/2018.
- large, for testing your actual models: 20 million ratings applied to 27,000 movies by 138,000 users. 
   This has been upoloaded to the cluster data store for you.
   
You will be using only one of the files in the dataset: **ratings.csv**.  The large version on the cluster has been stored as a parquet file, a binary format for Spark dataframes that is much faster to load than csv.

## Task 1: build a global recommendation model

- Start from the **task1** notebook provided (including loading  **ratings.paquet** into a dataframe
- train a recommender model using the ALS approach. You may refer to the example code on the [Spark doc for Collaborative Filtering](https://spark.apache.org/docs/latest/mllib-collaborative-filtering.html#examples). However be aware that the input data format may be different
- after you build the model, you need to add code to automatically optimise the *rank* hyperparameter, usiong RMSE as your performance metric. Report your best results in the notebook.

## Task 2: Build the user-user network.

* load up **ratings.parquet** again
* create a graph where:
  * for each pair of users _u1_, _u2_ there is an edge with associated weight _w_, where _w_ is the number of movies that both _u1_ and _u2_ have rated (regardless on the actual rating).
  * if _u1"_ and _u2_ have not got any rating in common, there is no edge between them.

It is important that you comply with the prescribed output format for the graph, because it is to be used as input for the next step.
In Spark memory, this is a dataframe with Schema

```(source_node, target_node, weight)```
    
example:    
```    source,target,weight
    1,6,1
    1,8,1
    2,3,1
    2,4,1
```
a small sample file is provided [here](data/edge_sample.csv). 

## Task 3: Community detection.

This task requires you to implement a version of the Girwan-Newman algorithm that is optimised to make use of multiple workers on the Spark clsuter.

You are given a python module that operates on the graoh structure you generated in Task 2, and implements: 
* SSSP (Single Source Shortest Path) 
* given a path between two nodes, compute the betweeness value for each of the edges along the path

You may start from notebook **task3** which has the required **import** statements

Using these methods, you will implement a version of GN that includes MapReduce patterns to parallelise execution on the entire graph.
Details on this step will have been given in class.

Report on the running for the algorithm both on the small and full datasets.

You will need to be careful how you implement this step, because an inefficient implementation will simply not scale to the size of the full dataset.

Note also that the number of communities you choose depends on the betweeness threshold. It is recommended that you do not generate more than 5 communities.

# Checkpointing.

In case you get stuck on this Task, a copy of its output (the community files) can be provided. You will get less than full  marks for this task, depending on your progress, but you will be able to progress to the next task.

## Task 4: Generate user-user sub-matrices for each community

Each community is a subgraph of the graph you generated in Task 2. For each of these, you need to extract the relevant rows and columns from the original U-M-R dataset, so that you can then train a recommender model for each of these communities (see next Task).

In practice, given a community graph you will simply select all rows that correspond to users in that community.

## Task 5:  build community-specific recommendation models

This is effectively the same as Task 1, but repreated for each sub-matrix as produced in Task 4. For each model, report its RMSE performance.

## Task 6: Compare models

In this final task you are required to compare performance results obtained in Task 1 and Task 5, and discuss the rationale for choosing either solution.
This is not a programming task but you are required to make notes in your notebook, and expect to discuss these during your viva.
   


# Prerequisite Packages

Packages|Version
---|---
networkx|2.2.0
matplotlib|>=3.0.1tin
pyspark|=2.3.0
pandas|>=0.23.0


## Details on of the Data Structures used in the assignment

**Graph**

This is a class you can import:

`from comscan.model.graph import Graph`

List of edges. It is loaded in memory as an adjacency list.

    [(source_node, target_node, weight)]
    
    source,target,weight
    1,6,1
    1,8,1
    2,3,1
    2,4,1

Note: in Task 4, each of your workers require a copy of the entire graph to compute on. You will need to use a `broadcast variable` to hold the graph instance

**Paths**

    {target: [path]}
    path = [node]

    {1: [[1]], 2: [[1, 2], [1, 3, 2]], 3: [[1, 3]], 4: [[1, 2, 4], [1, 3, 2, 4]], 5: [[1, 2, 4, 5], [1, 3, 2, 4, 5]], 6: [[1, 2, 4, 6], [1, 3, 2, 4, 6], [1, 2, 4, 5, 6], [1, 3, 2, 4, 5, 6], [1, 2, 4, 7, 6], [1, 3, 2, 4, 7, 6]], 7: [[1, 2, 4, 7], [1, 3, 2, 4, 7]], 8: []}


**Shortest Paths**

This RDD holds the result from an invocation of the SSSP algorithm:

    shortest_paths_rdd -> [(source, paths)]
    paths -> {target: [shortest_path]}
    shortest_path -> [node]
    source -> int
    target -> int
    node -> int

    [(1,
      {
       1: [[1]],
       2: [[1, 6, 2], [1, 8, 2]],
       3: [[1, 6, 2, 3], [1, 8, 2, 3], [1, 6, 4, 3]],
       4: [[1, 6, 4]],
       5: [[1, 6, 2, 5], [1, 8, 2, 5], [1, 8, 7, 5]]
      }
     )
    ]


**Edges count map**:

contains count of shortest paths to this target through this edge
 
    {target: {edge: edge_count}}
    
    {1: {}, 2: {(1, 2): 1.0, (3, 2): 1.0, (1, 3): 1.0}, 3: {(1, 3): 1.0}, 4: {(1, 2): 1.0, (3, 2): 1.0, (1, 3): 1.0, (2, 4): 2.0}, 5: {(1, 2): 1.0, (4, 5): 2.0, (3, 2): 1.0, (1, 3): 1.0, (2, 4): 2.0}, 6: {(1, 2): 3.0, (5, 6): 2.0, (3, 2): 3.0, (1, 3): 3.0, (4, 6): 2.0, (4, 5): 2.0, (7, 6): 2.0, (2, 4): 6.0, (4, 7): 2.0}, 7: {(1, 2): 1.0, (4, 7): 2.0, (1, 3): 1.0, (3, 2): 1.0, (2, 4): 2.0}, 8: {}}


**Betweenness**:

A  Dictionary of edges and their betweenness value (float) as generated based on one SSSP invocation, i.e., these will be _partial_ betweeness values

    {egdge: betweennes_value}
    
    {(1, 2): 2.5, (5, 6): 0.3333333333333333, (4, 7): 1.3333333333333333, (1, 3): 3.5, (2, 3): 2.5, (4, 6): 0.3333333333333333, (4, 5): 1.3333333333333333, (6, 7): 0.3333333333333333, (2, 4): 4.0}


**Communities**:

Set of node ids

    {node}
    {1,2,3} 

**Components**:

Each connected component in the graph is partitioned into communities. This is represented as:

    (community)
    ({1, 2, 3}, {4, 6}, {5}, {7}, {8})


**Edges Count RDD**

Contains count of shortests paths that go through each edge. Used to compute betweeness but you are not required to use it explicitly in the assignment.

**Paths Count RDD**

Contains the number of shortest paths between two nodes

    path_count_rdd -> [(source, target), paths_count]

    [
      ((1, 1), 1), 
      ((1, 2), 2), 
      ((1, 3), 3), 
      ((1, 4), 1), 
      ((1, 5), 3)
    ]

**Edge Betweenness RDD**

    edge_betweenness_rdd -> [(edge, betweenness)]
    edge -> (u,v)
    betweenness -> float

    [
      ((2, 8), 69.9047619047619),
      ((6, 12), 191.4793650793651),
      ((11, 15), 106.36190476190477),
      ((5, 22), 135.8968253968254),
      ((13, 14), 45.63809523809524)
    ]

## Benchmark -- expected execution times.

Edges: 3000;		Target Level: 5;			Sequential Computing Time (seconds): 298.97922587394714 \
Edges: 1000;		Target Level: 5;			Distributed Computing Time (seconds): 78.53743696212769 \
Edges: 2000;		Target Level: 5;			Distributed Computing Time (seconds): 334.11402106285095 \
Edges: 2000;		Target Level: 5;			Sequential Computing Time (seconds): 112.116375207901 \
Edges: 1000;		Target Level: 5;			Sequential Computing Time (seconds): 25.027655601501465

## References

1. Girvan M. and Newman M. E. J., Community structure in social and biological networks, Proc. Natl. Acad. Sci. USA 99, 7821–7826 (2002).
2. Freeman, L., A Set of Measures of Centrality Based on Betweenness, Sociometry 40, 35–41  (1977).
3. E. W. Dijkstra, A note on two problems in connexion with graphs. Numerische Mathematik, 1:269–
271, (1959)
4. GitHub - networkx/networkx: Official NetworkX source code repository, https://github.com/networkx/networkx
5. Takács, G. and Tikk, D. (2012). Alternating least squares for personalized ranking. 
Proceedings of the sixth ACM conference on Recommender systems - RecSys '12. 
[online] Available at: https://www.researchgate.net/publication/254464370_Alternating_least_squares_for_personalized_ranking
