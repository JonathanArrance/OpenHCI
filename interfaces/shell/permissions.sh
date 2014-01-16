#!/bin/bash -x
usermod -a -G postgres admin
usermod -a -G nova admin
usermod -a -G cinder admin
usermod -a -G glance admin
usermod -a -G swift admin
usermod -a -G quantum admin
usermod -a -G keystone admin