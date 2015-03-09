# Dynamic-EC2-Reservation

You've taken the big step and bought some reserved instances! Let's say
you bought two. Unfortunately, your autoscaling group can deploy to
three different AZs and you don't want to have to move your reserved
instances around by hand every time you rebuild a server. That's where
Dynamic-EC2-Reservation comes in.

In the style of
[dynamic-dynamodb](https://github.com/sebdah/dynamic-dynamodb) it
provides a fix for something Amazon really should abstract away.
