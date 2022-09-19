  # D2 Weapon Predictions
  
  This is my attempt at building a Machine Learning model to accurately predict the archetype of a weapon from Destiny 2 given its characteristics.

  There are 4 models currently being tested including:

  - Stats only
  - Stats + Element type
  - Stats + Ammo type
  - Stats + Ammo type + Element type

  These models are tested against the weapon type and the weapon type + frame type (8 predictions)

  All data is pulled from Destiny's API via the great work by [altbdoor](https://altbdoor.github.io/d2-api-human/)!
  
  This README will be updated as new features become available! Stay tuned!

  ## Future goals

  - Add perk pools to predictions to see if that alters prediction reliability
  - Try to predict weapon rarity given stats (or anything else)
    - Can combine any of the other future goals with this one too

  ## Completed Updates

  ### 9/18/2022

  - Increase difficulty of prediction by removing certain columns (ammo type and/or element type)
    - Note: Element type was a curiosity, it was not expected to affect model performance
  - Use models to predict weapon type + frame
