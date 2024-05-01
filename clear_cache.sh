#!/bin/bash
cd `dirname $0`
trash cache.json || mv cache.json cache.json.old
echo "that's cash, in the trash"