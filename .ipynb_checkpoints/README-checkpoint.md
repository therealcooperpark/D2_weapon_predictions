  # D2 Weapon Predictions
  
  This is my attempt at building a Machine Learning model to accurately predict the archetype of a Legendary (purple) weapon from Destiny 2 given its characteristics. Characteristics include:
  
  - All weapon stats (e.g., Handling, Range, Aim Assistance, etc.)
  - Ammo type (e.g., Primary, Special, Heavy)
  - Element Class (e.g., Arc, Solar, Void, Stasis)
  
This dataset is trained and tested against several ML models:

  - Decision Trees
  - Logistic Regression
  - Bagging
  - Random Forest
  - Gradient Boosting
  - Adaptive Boosting
  
These models are trained to predict the weapon archetype (e.g., Shotgun, Hand Cannon, etc.) of each weapon.

  All weapon data is pulled from Destiny's API via the great work by [altbdoor](https://altbdoor.github.io/d2-api-human/)!
  
  This README will be updated as new features become available! Stay tuned!

  ## Future goals

  - Add perk pools to predictions to see if that alters prediction reliability
  - Train models to predict weapon archetype & frame together
  - Train models to predict weapon rarity
  - Add Hyperparameter tuning
  - Add model saving and customization options
  - ~~Add additional prediction algorithms~~ **Complete as of 9/20/22**
  - ~~Add additional reported statistics~~ **Complete as of 9/28/22**
  

  ## Completed Updates
  
  ### 9/28/2022
  - Converted code base to a Jupyter Notebook to improve readability and modularization of ML steps.
  - Finalized statistic reporting of model training/testing (until hyperparameter tuning is built)
  
  ### 9/21/2022
  - Included additional reported statistics in the form of a confusion matrix for each model (still tweaking for consistency)
  - Added boxplot comparing cross-validation values across all tested models

  ### 9/20/2022

  - Overhaul of code base including:
    - Refactor of dataset and model building
    - Can build and test multiple models
    - Basic statistics comparison with cross-validation and validation based on precision

  ### 9/18/2022

  - Increase difficulty of prediction by removing ammo type
  - Use models to predict weapon type + frame
