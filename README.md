# manual_ml_feedback

This provides an interface for a labeler to give feedback to the ML model. I does so in several steps:

1) It presents previously classified images for label checking with any detected distress patches for boards, tarps and general istress.
2) Once the labeler has made their way through the image dataset, the program automatically saves the images to the image stores specified in the yaml config file. 
3) Finally, all ML models are retrained so long as the datasets meet a threshold of change specified in the config file. 
4) Logging documents will be generated such as the validation accuracy of the new model and a dataset log and hash of all files used when training it. If the validation set does better than the current best, the model replaces the one currently in autoclassify.