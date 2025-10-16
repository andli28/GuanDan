- We use several "magic numbers" (e.g., 300, 400, 100, 500, 1000) as base ranks for card combinations. This makes the ranking logic difficult to understand, compare, and maintain. These values should be extracted into named constants (e.g., RANK_BASE_BOMB_4, RANK_BASE_STRAIGHT_FLUSH) to improve code clarity and make future adjustments to the ranking system safer and easier.

- Update the README with instructions on how to run this code
- how to install the installable package instead using uv
- pytest to test it.

- Add pytest to github actions