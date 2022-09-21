  # D2 Weapon Predictions
  
  This is my attempt at building a Machine Learning model to accurately predict the archetype of a weapon from Destiny 2 given its characteristics.

  There are 2 models currently being tested, including:

  - Stats only
  - Stats + Ammo type

  These models will be tested against the weapon type and the weapon type + frame type (8 predictions)

  All data is pulled from Destiny's API via the great work by [altbdoor](https://altbdoor.github.io/d2-api-human/)!
  
  This README will be updated as new features become available! Stay tuned!

  ## Future goals

  - Add perk pools to predictions to see if that alters prediction reliability
  - Try to predict weapon rarity given stats (or anything else)
    - Can combine any of the other future goals with this one too
  - Add additional prediction algorithms
  - Add additional reported statistics
  - Add comparative measurements between algorithms/models
  - Add model saving and customization options

  ## Completed Updates

  ### 9/20/2022

  - Overhaul of code base including:
    - Refactor of dataset and model building
    - Can build and test multiple models
    - Basic statistics comparison with cross-validation and validation based on precision

  ### 9/18/2022

  - Increase difficulty of prediction by removing ammo type
  - Use models to predict weapon type + frame
