
# Write a collision checker

In this exercise, you will write a collision checker. In the next exercise you will use this collision checker as part of a planning algorithm.

Note: This is a code-only exercise: you don't need the Duckiebot.



## Instructions

The template contained in this folder is a fully functional (wrong) solution. Currently, the solution submits random guesses as to whether the robot collides with the environment or not. You can try to evaluate right away to see how it works.

Make sure you have an updated system using

    dts desktop update

To evaluate the submission,  go in `collision_checker` and use:

    dts challenges evaluate --challenge mooc-collision-check-vali 

To submit, use

    dts challenges submit

Note that the submission will be sent to two different challenges:

- [`mooc-collision-check-vali`][vali] is the **validation** challenge. You will be able to see the score and other output.
- [`mooc-collision-check-test`][test] is the **testing** challenge. You will not be able to see the scores.

To pass, you have to get at least 95% of the queries correct on the `mooc-collision-check-test` challenge. (This allows some slack, so that you can experiment with probabilistic algorithms).

Note that you cannot do

    dts challenges evaluate --challenge mooc-collision-check-test  !! does not work !!

because the test challenge must remain a secret.

[test]: https://challenges.duckietown.org/v4/humans/challenges/mooc-collision-check-test
[vali]: https://challenges.duckietown.org/v4/humans/challenges/mooc-collision-check-vali

Now, start the jupyter notebook with 

`dts exercises lab` and open the notebook `collision_checker01.ipynb` and have a look at `collision_checker.py`, which contains the template.

Modify the file and test if the program runs or check its performance with local evaluations over the validation dataset. And once satisfied with the program, submit to the challenge.

