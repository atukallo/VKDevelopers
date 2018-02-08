# Developers in vk

The repository contains script, that analyzes users of the vk.com social network and determines if they are interested in programming.

You can start crawling from any vk-id and script will perform bfs on friends of that vk-id until it finds enough programmers. Moreover, specific programming language can be specified to filter developers according to preferred language. 

Every user gets a score based on his subscriptions, career history, education, github account (if present), etc. Then score is compared to a threshold to determine if we can consider user a programmer. 
