#!/bin/bash

CONFIG_PATH=/data/options.json

if [ ! $PHONE_NUMBER ] && [ -f $CONFIG_PATH ]; then
    PHONE_NUMBER=$(jq --raw-output '.phoneNumber' $CONFIG_PATH)
fi

if [ ! $PHONE_NUMBER ] || [ null == $PHONE_NUMBER ]; then
    echo "error! phoneNumber is null"
    exit 1
fi

if [ ! $PASSWORD ] && [ -f $CONFIG_PATH ];then
    PASSWORD=$(jq --raw-output '.password' $CONFIG_PATH)
fi

if [ ! $PASSWORD ] || [ null == $PASSWORD ]; then
    echo "error! password is null"
    exit 1
fi

if [ ! $LOG_LEVEL ] && [ -f $CONFIG_PATH ]; then
    LOG_LEVEL=$(jq --raw-output '.logLevel' $CONFIG_PATH)
fi

if [ ! $LOG_LEVEL ] || [ null == $LOG_LEVEL ];then
    LOG_LEVEL=INFO
fi


if [ ! $HASS_URL ]; then
    HASS_URL=`sed '/^SUPERVISOR_URL = /!d;s/.* "//;s/"//' const.py`
fi

if [ ! $HASS_TOKEN ]; then
    HASS_TOKEN=$SUPERVISOR_TOKEN
    if [ ! $HASS_TOKEN ]; then
        echo "error! hass token is null"
        exit 1
    fi
fi

python3 ./main.py --PHONE_NUMBER=$PHONE_NUMBER --PASSWORD=$PASSWORD --LOG_LEVEL=$LOG_LEVEL --HASS_URL=$HASS_URL --HASS_TOKEN=$HASS_TOKEN
