# Film Festival Manager
#### Video Demo: https://www.youtube.com/watch?v=LKm3pMV__2U
#### Description:
The Film Festival Manager is a Flask application for managing the various components of a Film Festival. I wanted to make something that utilized user roles, which I have achieved to a limited degree. All of the configuration is managed by the “Admin” user role. All of the submission evaluations are handled by the “Evaluator” user role. The roles work, but I was left feeling like I could benefit from spending a lot of time researching how best to implement roles outside of a simple string value on a user record.

As an “Admin”, users can create  several film festival components:
- Events → A record that is used as an attribute on categories and submissions
- Categories → A record that is used as an attribute on submissions and which has configurable evaluation criteria
- Evaluation Criteria → A record that is used as an attribute on categories to define what criteria evaluators will see when evaluating  a submission from that category
- Submissions → A record representing all of the metadata and attributes for a film festival submission

Additionally, an “Admin” user can see all evaluations from all evaluators and make some changes to users, such as user roles, user categories, user name, and user status.

As an “Evaluator”, users can create an evaluation against submissions for the categories that they are assigned. Their view is much simpler and is limited to a page containing all submissions available to them that have not been evaluated yet and another to view and edit all of their evaluations.

All of this functionality is split across multiple files. I created two main paths for these users in my templates and utilized Flask's blueprints to add a certain degree of modularity to the application. This was helpful, but it was also a new technology that I was learning while implementing. Overall, I think there are a lot of areas that could be improved.

There is a lot of room for improvement here. I was still dependent on the cs50 library for all my SQL needs. I would like to look at `sqlalchemy` in the future. I also learned about some database management best practices that I would like to refactor at some point, specifically the naming convention for utilizing singular table names.

Overall, I think my project could be better organized, both structurally and from a code perspective. I have a tednency to get stuck on small details, so I tried to push past through a lot of that and get to a true MVP for my project. There was a lot of "code smell", but I didn't let that keep me from progressing forward. I am proud of what I was able to accomplish in the time that I had. I will be continuing a few personal projects after this class and will be utilizing all that I have learned in CS50.

Thanks! :)

-p
