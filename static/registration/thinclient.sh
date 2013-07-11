#!/bin/sh
xdg-open "http://kurre.soberit.hut.fi:8080/registration/$(hcitool dev | grep hci0  | sed 's/hci0//' | sed 's/^[ \t]*//' )/"
