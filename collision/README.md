
# Write a collision checker

In this exercise, you will write a collision checker. In the next exercise you will use this collision checker as part of a planning algorithm.

Note: This is a code-only exercise: you don't need the Duckiebot.


* [Instructions](#instructions)
* [Data structures and protocol](#data-structures-and-protocol)
* [Tips for implementing the collision checker](#tips-for-implementing-the-collision-checker)
  + [Use decomposition](#use-decomposition)
  + [Pay attention to the poses](#pay-attention-to-the-poses)
  + [In the end, what is the core complexity?](#in-the-end--what-is-the-core-complexity-)
  + [Speeding things up using lower/upper bound heuristics](#speeding-things-up-using-lower-upper-bound-heuristics)
  + [Speeding things up using bitmaps heuristics](#speeding-things-up-using-bitmaps-heuristics)
* [Submtting](#submitting)


## Instructions

The template contained in this folder is a fully functional (wrong) solution. Currently, the solution
submits random guesses as to whether the robot collides with the environment or not. You can try to 
evaluate right away to see how it works.

Make sure you have an updated system using

    dts desktop update

To evaluate the submission,  go in `collision_checker` and use:

    dts challenges evaluate --challenge mooc-collision-check-vali 

Note: Sometimes this command will take longer than you expect.

The command line will specify where the evaluation output is saved. The challenges output will 
be a series of images. In the `queries` folder you will see the queries with the ground truth, where
each query is a robot position. Each image shows all the queries for each environment.

Colors:
- Blue is a pose in which the robot does not collide.
- Red is a pose in which the robot collides.

![query](env18.png)

In the `results` folder you will see your results and the errors you made:

Colors:
- Blue is a pose in which the robot does not collide and you guessed RIGHT.
- Orange is a pose in which the robot does not collide and you guessed WRONG.
- Red is a pose in which the robot collides and you guessed RIGHT.
- Pink is a pose in which the robot collides and you guessed WRONG.

![result](env18-result.png)

Your goal is to make sure that your collision guesses accurately match the ground truth. In other terms, 
you are trying to get to a false-positive(Orange) rate of 0% and a false-negative(Pink) rate of 0%.

To get started writing the collision checker, go read `collision_checker.py`, which contains the template. 
There are some hints to get started there. Modify the file and check its performance with the `evaluate`
command above. 

For information on the [Data Structures](#data-structures) used or the [CollisionChecker protocol](#collisionchecker-protocol), see the corresponding sections below. For some [tips for implementing the collision checker](#tips-for-implementing-the-collision-checker), go to the corresponding section below.

Once you are satisfied with the program, [submit](#submitting) to the challenge with the section below.

## Data structures

The data structures are defined in the `dt-protocols-daffy` package, which you can install via `pip`, or directly 
clone from [repo][repo].
[repo]: https://github.com/duckietown/dt-protocols

In particular, you can see in [`collision_protocol.py`][file] the data structures to use.

[file]: https://github.com/duckietown/dt-protocols/blob/daffy/src/dt_protocols/collision_protocol.py

The parameters for the collision checker is a `MapDefinition`, which specifies the `environment` and `body`. 
The `environment` is all of the shapes that the robot can collide with, and the `body` is all of the shapes that
make up the robot's body. Therefore, both `environment` and `body` are lists of `PlacedPrimitive`s. However, in
the validation tests, the robot will only be made up of one `PlacedPrimitive`.

A `PlacedPrimitive` is a pair of a `FriendlyPose` and a `Primitive`, or a pose and a shape. Note that `theta_deg` in
`FriendlyPose` starts at zero in the positive x-axis direction and ends at 359 degrees, moving in a counter-clockwise 
direction.

```python
@dataclass
class PlacedPrimitive:
    pose: FriendlyPose
    primitive: Primitive
    
    
@dataclass
class FriendlyPose:
    x: float
    y: float
    theta_deg: float
```

A `Primitive` is either a `Rectangle` or a `Circle`. A circle's shape needs only be defined
by a `radius`, while a Rectangle is defined by four values:
 - `xmax` is the distance from the pose point to its side in the positive x direction (if theta_deg in `FriendlyPose` is zero, this side is on the right of the pose point).
 - `xmin` is the same, but in the negative x direction
 - `ymax` is the distance from the center point to its side in the positive y direction (if theta_deg in `FriendlyPose` is zero, this side is on the top of the pose point).
 - `ymin` is the same, but in the negative y direction

```python

@dataclass
class Circle:
    radius: float


@dataclass
class Rectangle:
    xmin: float
    ymin: float
    xmax: float
    ymax: float

Primitive = Union[Circle, Rectangle]
```

So, we represents shapes as the union of rototranslated `Rectangle`s and `Circle`s.

## CollisionChecker Protocol

The class `CollisionChecker` in `collision_checker.py` first receives a message `MapDefinition` to define the environment and robot shape. Then, it recieves a sequence of `CollisionCheckQuery`s. The query contains a pose for the robot.

The code you will write should take the pose in the `CollisionCheckQuery`, combine it with the robot shape from the `MapDefinition`, and then see if it collides with any part of the environment. The result of this will go into a `CollisionCheckResult`. The `CollisionCheckResult` contains only a boolean: true means that it is in collision, false means that it is not in collision.

## Tips for implementing the collision checker

There are multiple ways to implement the collision checker. Here are some tips, but feel free to follow your intuition or change it
up as you see fit.

### Use decomposition

The first thing to note is that the problem can be *decomposed*.

You are asked to see whether the robot collides with the environment at a certain pose.
The robot is a list of `PlacedPrimitive` and the environment is a list of `PlacedPrimitive`s. Remember, 
a `PlacedPrimitive` is the combination of a pose and a primitive, or in other terms, a location and
a shape. In pseudocode:

    robot =  rp1 ∪ rp2 ∪ rp3 ∪ ...
    environment =  obj1 ∪ obj2 ∪ obj3 ∪ ...

(Note: In the validation tests, the robot is only ever composed of one shape. But it's good to program this
to work with multiple shapes so you could work with more complex robot designs.)

What you have to check is whether the intersection

    robot ∩ environment

is empty. By substituting terms we obtain:

    (rp1 ∪ rp2 ∪ ...) ∩ (obj1 ∪ obj2 ∪ ...)

Now, the intersection of unions is a union of intersection:

    [rp1 ∩ (obj1 ∪ obj2 ∪ ...)]  ∪  [rp2 ∩ (obj1 ∪ obj2 ∪ ...)] ∪ ...

The above shows that you have to check whether any primitive of the robot collides with environment.

Further expanding the first term we obtain:

    [rp1 ∩ (obj1 ∪ obj2 ∪ ...)] = (rp1 ∩ obj1) ∪ (rp2 ∩ obj2) ∪ ...

This shows that in the end, you can reduce to problem to checking pairwise intersection of `PlacedPrimitives`. 
Therefore, using *decomposition*, we have simplified the problem of "Does the robot collide with 
the environment?" to asking "Does this part of the robot collide with this environmental object?". We ask
this second question multiple times for each query. If the answer to this second question is ever yes, then 
we know that the robot collides with the environment.

This tip has already be partially implemented in `collision_checker.py`.

### Pay attention to the poses

Both robot and environment are lists of `PlacedPrimitives`.

That is, we should rewrite the robot expression as:

    robot = RT(pose1, primitive1) ∪ RT(pose2, primitive1) ∪ ...

where `RT()` rototranslates a primitive by a pose. Also note that for each 
query the robot changes pose. Let's call this pose `Q`. Note that we have:

    robot at pose Q = RT(Q * pose1, primitive1) ∪ RT(Q * pose2, primitive1) ∪ ... 

where `Q * pose` represent matrix multiplication. You will need to implement
this functionality in the `check_collision()` function of `collision_checker.py`.

### In the end, what is the core complexity?

Following the above tips, you should be able to get to the point where you are left with checking the collision of two rototranslated primitives. Therefore, the core complexity is this: How do you determine if two `PlacedPrimitives` are colliding?

Now notice that there are 3 cases:
- `Circle` vs `Circle`
- `Rectangle` vs `Circle`
- `Rectangle` vs `Rectangle`

Note that without loss of generality you can get to the point where you have one primitive at the origin (You put one primitive in the coordinate frame of the other). How would you go about it?

`Circle` vs `Circle` is easy: two circles intersects if the distance of the centers is less than the sum of the radii. (The validation tests don't actually ever use a circle shape on a robot, so this case may seem unncessary, but it's useful to leave it in for learning purposes).

For the others, you have to think about it... Use your robotic mind to engineer a solution! It needs to be correct 95% of the
time in order to pass the submission below, but the goal is to have 100% accuracy. This will lead to your planning algorithm in
the next exercise having better performance, and you might be able to get high up on the [leaderboards](https://challenges.duckietown.org/v4/humans/challenges/mooc-collision-check-test/leaderboard)!

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

## Submitting

To submit, use

    dts challenges submit

Note: Sometimes this command will take longer than you expect.

Note that the submission will be sent to two different challenges:

- [`mooc-collision-check-vali`][vali] is the **validation** challenge. You will be able to see the score and other output.
- [`mooc-collision-check-test`][test] is the **testing** challenge. You will not be able to see the scores.

To pass, you have to get at least 95% of the queries correct on the `mooc-collision-check-test` challenge. (This allows some slack, so that you can experiment with probabilistic algorithms).

Note that you cannot do

    dts challenges evaluate --challenge mooc-collision-check-test  !! does not work !!

because the test challenge must remain a secret.

[test]: https://challenges.duckietown.org/v4/humans/challenges/mooc-collision-check-test
[vali]: https://challenges.duckietown.org/v4/humans/challenges/mooc-collision-check-vali