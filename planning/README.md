
# Write a path planner

In this series of exercises, you will write path planners of increasing complexity. 

You need to have solved the `collision` exercise, because you will need a collision checker. 

Note: This is a code-only exercise: you don't need the Duckiebot.

 

## Path planning problems 

We will consider several variations of path planning problems.

There are **two complexity axes**: dynamic constraints and environment complexity.


For **dynamic constraints** we have 2 cases:

1. The basic case is that of a differential drive robot, which can turn in place. 
2. The advanced case is a car-like dynamics: the robot cannot turn in place, because there is a bound on the maximum path curvature.

For **environment complexity** we have 3 cases:

1. The basic case is that of an **empty** environment.
2. The intermediate case is that of an environment with **static** obstacles.
3. The advanced case is that of an environment with **dynamic** obstacles (with known motion).

After the "Planning 1" and "Planning 2" modules, you should be able to do the challenges *without the curvature constraints*.

For the challenges with the curvature constraints, you need an understanding of the materials in "Planning 3".

The combinations give rise to 6 challenges, summarized in the following table.


| challenge                                                      | dynamic constraints     | environment        | MOOC modules   |
|----------------------------------------------------------------|-------------------------|--------------------|----------------|
| [mooc-planning-dd-empty-vali][mooc-planning-dd-empty-vali]     | differential drive      | empty              | Planning 1,2   |
| [mooc-planning-cc-empty-vali][mooc-planning-cc-empty-vali]     | + curvature constraints | empty              | Planning 1,2,3 |
| [mooc-planning-dd-static-vali][mooc-planning-dd-static-vali]   | differential drive      | static obstacles   | Planning 1,2   |
| [mooc-planning-cc-static-vali][mooc-planning-cc-static-vali]   | + curvature constraints | static obstacles   | Planning 1,2,3 |
| [mooc-planning-dd-dynamic-vali][mooc-planning-dd-dynamic-vali] | differential drive      | dynamic obstacles  | Planning 1,2   |
| [mooc-planning-cc-dynamic-vali][mooc-planning-cc-dynamic-vali] | + curvature constraints | dynamic obstacles  | Planning 1,2,3 |

[mooc-planning-dd-empty-vali]:
[mooc-planning-cc-empty-vali]:
[mooc-planning-dd-static-vali]:
[mooc-planning-cc-static-vali]:
[mooc-planning-dd-dynamic-vali]:
[mooc-planning-cc-dynamic-vali]:

(Except for the first two, there are also corresponding `-test` challenges with hidden traces that are used for grading.)


## Instructions

The template contained in the `planner` subfolder is a fully functional (but wrong) solution.

You can try to evaluate/submit it right away.

Make sure you have an updated system using

```shell 
dts desktop update
```

To evaluate the submission, go in `planner/` and use:

```shell 
dts challenges evaluate --challenge mooc-planning-dd-static-vali
```

To submit, use

```shell
dts challenges submit
```

This will send it to all the challenges listed in the `submission.yaml` file (all of the above).

To minimize confusion, you might want to submit to one challenge at a time with the `--challenge` option.


### Passing criteria

Note that for the Spring 2021 MOOC this is not a graded exercise.

To pass, you have to get at least 95% of the queries correct on the `*-test` challenges.
(This allows some slack, so that you can experiment with probabilistic algorithms).

 
## Data structures and protocol

The data structures are defined in the `dt-protocols-daffy` package, which you can install via `pip`, or directly clone from the [repo][repo].
Note that from time to time we make changes to the code, so if there are weird errors try to update the version that you have .




[repo]: https://github.com/duckietown/dt-protocols


Now, go read `planner.py`, which contains the template. There are some hints to get started there. 

Modify the file and test if the program runs or check its performance with local evaluations over the validation dataset. And once satisfied with the program, submit to the challenges.
 

In particular, you can see in [`collision_protocol.py`][file] the data structures to use.

[file]: https://github.com/duckietown/dt-protocols/blob/daffy/src/dt_protocols/collision_protocol.py


Note: The data structures used for the planner are an extension of the data structures used in the `collision` exercise. 
Please refer to that documentation for a description of `PlacedPrimitive`, `FriendlyPose`, `Primitive`, `Rectangle`, `Circle`, etc.


This is the protocol:

1. The planner receives first a message of type `PlanningSetup`, which contains a description of the environment, the robot body, and the dynamic constraints.
2. Then the planner receives a sequence of `PlanningQuery`s. The query contains a start and a target pose for the robot. 
3. The planner must respond with a `PlanningResult` message containing the  plan.

More in detail:

The `PlanningSetup` object is an extension of the `MapDefinition` type used in the previous exercise. `MapDefinition` contains 
a description of the environment and robot body. `PlanningSetup` extends it with the planning constraints.

```python
@dataclass
class PlanningSetup(MapDefinition):
    bounds: Rectangle
    max_linear_velocity_m_s: float
    min_linear_velocity_m_s: float
    max_angular_velocity_deg_s: float
    max_curvature: float
    tolerance_xy_m: float
    tolerance_theta_deg: float
```

Environment:

* `bounds` is a `Rectangle` that gives the overall area where the robot is allowed.

Dynamic constraints:

* `min_linear_velocity_m_s` and `max_linear_velocity_m_s` give the interval of linear velocity allowed in the x direction (in m/s).
* `max_angular_velocity_deg_s` is the maximum turning rate (in deg/s)
* `max_curvature` is the maximum curvature allowed. Example: if `max_curvature` is 4, it means that the smallest circle that the robot can trace is 1/4 = 0.25 m.

Tolerances:

* `tolerance_xy_m` is the maximum tolerance for errors in the final pose for x-y.
* `tolerance_theta_deg` is the maximum tolerance for errors in the final pose for the orientation.

The `PlanningQuery` message contains the start and target pose:

```python
@dataclass
class PlanningQuery:
    start: FriendlyPose
    target: FriendlyPose
```

The `PlanningResult` message is:

```python
@dataclass
class PlanningResult:
    feasible: bool
    plan: Optional[List[PlanStep]]
```

In your response, you should first declare if you found a feasible solution with the first boolean.
(Note that in the scoring we penalize if you declared that you found a feasible solution when you don't have it more that if you just declare it infeasible).

In case of a feasible answer, you should return the plan, which is a list of `PlanStep`s.

A `PlanStep` contains the duration of the step as well as angular and linear velocity held constant during the step:

```python
@dataclass
class PlanStep:
    duration: float
    velocity_x_m_s: float
    angular_velocity_deg_s: float
```

As an example, this is an example (contained in the planner template) that describes a plan to trace a square:


```python
# Let's trace a square of side L at maximum velocity.
L = 1.0
duration_straight_m_s = L / self.params.max_linear_velocity_m_s
duration_turn_deg_s = 90.0 / self.params.max_angular_velocity_deg_s

# The plan will be: straight, turn, straight, turn, straight, turn, straight, turn

straight = PlanStep(duration=duration_straight_m_s, angular_velocity_deg_s=0.0,
                    velocity_x_m_s=self.params.max_linear_velocity_m_s)
turn = PlanStep(duration=duration_turn_deg_s,
                angular_velocity_deg_s=self.params.max_angular_velocity_deg_s,
                velocity_x_m_s=0.0)

plan = [straight, turn] * 4

```

### Extension: moving obstacles

The new thing that is introduced in these exercises is that now a `PlacedPrimitive` can have an optional `Motion` object associated, which, if not equal to `None`, specifies its path in time.

```python
@dataclass
class PlacedPrimitive:
    pose: FriendlyPose
    primitive: Primitive
    motion: Optional[Motion]  # new!
```


The motion is described as a sequence of `PlanStep`:

```python
@dataclass
class Motion:
    steps: List[PlanStep]
```

(Note here that we are doing motion planning in dynamic environments with *known* motion. 
Studying reactive cases in which agents react to )


In the `dt_protocols` module you will find a useful function `simulate` which you can use to predict the trajectories for the obstacles (and for yourself as well):

```python

@dataclass
class SimulationResult:
    poses: List[FriendlyPose]
    ts: List[float]

def simulate(start: FriendlyPose, steps: List[PlanStep]) -> SimulationResult:
    """ Applies the plan to an initial pose to obtain a sequence of time/poses. """
```







Both `environment` and `body` are lists of `PlacedPrimitive`s.

A `PlacedPrimitive` is a pair of a `FriendlyPose` and a `Primitive`.
 





## Visualization

The challenges output will be a series of images.

In the `queries` folder you will see the queries with the ground truth,
as the image shows.

![query](sample/queries/env18.png)

Colors:

- Blue is a pose in which the robot does not collide.
- Red is a pose in which the robot collides.

In the `results` folder you will see your results and the errors you made:

![result](sample/results/env18-result.png)

The colors mean the following:

- Blue is a pose in which the robot does not collide and you guessed RIGHT.
- Orange is a pose in which the robot does not collide and you guessed WRONG.
- Red is a pose in which the robot collides and you guessed RIGHT.
- Pink is a pose in which the robot collides and you guessed WRONG.

## Tips for implementing the planner

There are multiple ways to implement the collision checker. Here are some tips, but feel free to follow your intuition.

### Use decomposition

The first thing to note is that the problem can be *decomposed*.

You are asked to see whether the robot collides with the environment at a certain pose.
Both robot and environment are lists of `Primitive`s. In pseudocode:

    robot =  rp1 ∪ rp2 ∪ ... 
    Wcoll =  wc1 ∪ wc2 ∪ ...

What you have to check is whether the intersection

    robot ∩ Wcoll 

is empty. Expanding:

    (rp1 ∪ rp2 ∪ ... ) ∩ (wc1 ∪ wc2 ∪ ...)

Now, the intersection of unions is a union of intersection:

    [rp1 ∩ (wc1 ∪ wc2 ∪ ...)]  ∪  [rp2 ∩ (wc1 ∪ wc2 ∪ ...)] ∪ ...

The above shows that you have to check whether any primitive of the robot collides with environment.

Further expanding the first term we obtain:

    [rp1 ∩ (wc1 ∪ wc2 ∪ ...)] = (rp1 ∩ wc1) ∪ (rp2 ∩ wc1) ∪ ...

which shows that in the end, you can reduce the problem to checking pairwise intersection of primitives.

### Pay attention to the poses

Both robot and environment are lists of **rototranslated** primitives.

That is, we should rewrite the robot expression as:

    robot = RT(pose1, primitive1) ∪ RT(pose2, primitive1) ∪ ...

where `RT()` rototranslates a primitive by a pose.

Also note that for each query the robot changes pose. Let's call this pose `Q`.

Note that we have

    robot at pose Q = RT(Q * pose1, primitive1) ∪ RT(Q * pose2, primitive1) ∪ ... 

where `Q * pose` represent matrix multiplication.

The above says that you can "push inside" the global pose.


### In the end, what is the core complexity?

Following the above tips, you should be able to get to the point where you are left with checking the collision of two rototranslated primitives.

Note that without loss of generality you can get to the point where you have one primitive at the origin. (You put one primitive in the coordinate frame of the other.)

Now notice that there are 3 cases:

- `Rectangle` vs `Circle`
- `Rectangle` vs `Rectangle`
- `Circle` vs `Circle`

`Circle` vs `Circle` is easy: two circles intersects if the distance of the centers is less than the sum of the radii.

For the others, you have to think about it...

 

### Speeding things up using lower/upper bound heuristics

If you want to speed things up, consider the following method, which allows to introduce a fast heuristic phase using only circle-to-circle comparisons.

For each rectangle `R`, you can find `C1`, the largest circle that is contained in the rectangle, and `C2`, the smallest circle that contains the rectangle. These are an upper bound and a lower bound to the shape.

    C1 ⊆ R ⊆ C2

Now notice that:

- if `C1` collides with a shape, also `R` does.  (but if it doesn't you cannot conclude anything)
- if `C2` does not collide with a shape, `R` does not as well. (but if it does, you cannot conclude anything)

Using this logic, you can implement a method that first checks quickly whether the circle approximations give already enough information to conclude collision/no-collision. Only if the first test is inconclusive you go to the more expensive component.

### Speeding things up using bitmaps heuristics

Another approach is using bitmaps to convert the environment to an image, where a black pixel means "occupied", and a white pixel means "free". 

Then you can do the same with the robot shape and obtain another bitmap.

Then you check whether the two bitmaps intersect

Advantages:

- reduces the problem of collision to drawing of shapes;
- cheaper if shapes are very complex.

Disadvantages:

- There are subtle issues regarding the approximations you are making. What exactly does a pixel represent? is it a point, or is it an area? is this an optimistic or pessimistic approximation? The semantics of painting is unclear. 


