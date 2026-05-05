#!/bin/bash

WDIR='./QuESO/'
#$INPUT_DIR
ODIR=$(realpath $WDIR/../docs/docsrc)
IGNORE=$(realpath $WDIR/.ignore)
APIDOC=$(echo $ODIR/api-reference.rst)

DETAIL="detail: "
RETURN="return (type): "
METHOD="method: "
FNTEST="test-method:"

FILE="file: "
LANG="lang: "
SYNOPSIS="synopsis: "
AUTHOR="author: "

TITLE="API Reference"

repeat(){
    for ((i = 0; i < $2; i++)); do echo -n "$1"; done
}

topwrite() {
    [ "$(wc -l < $2)" -gt 0 ] || printf '\n' >> $2
    if [ $(cat $2 | grep -c "$FILE") -eq 0 ]; then
        sed -i -e "1i$1> $FILE ${2%.*}" $2
    fi
    if [ $(cat $2 | grep -c "$LANG") -eq 0 ]; then
        sed -i -e "2i$1> $LANG $3" $2
    fi
    if [ $(cat $2 | grep -c "$SYNOPSIS") -eq 0 ]; then
        sed -i -e "3i$1> $SYNOPSIS" $2
    fi
    if [ $(cat $2 | grep -c "$AUTHOR") -eq 0 ]; then
        sed -i -e "4i$1> $AUTHOR $FYX_USERNAME <$FYX_EMAIL>" $2
    fi
}

IGSTR=""
if [[ -e $IGNORE ]]; then
    echo -e ".ignore file detected"
    while read -r line; do
        Line="$(echo $line | tr -d '\r')"
        IGSTR+="-not -regex $WDIR/$Line.* "
    done < "$IGNORE"
fi

OUT=$(eval "find $WDIR $IGSTR -type f -print")
DIR=($OUT)

INPUT_TYPE="gen"

case $INPUT_TYPE in
    "gen")
        for i in ${DIR[@]}; do
            ii=${i##*/}
            if ! [[ $(jq ".lang.${ii##*.}" ./style.json) == null ]]; then
                c=$(jq ".lang.${ii##*.}.comment" ./style.json | tr -d '\"' )

                test=$(jq ".lang.${ii##*.}.function.tag" ./style.json | tr -d '[]\"[:space:]')
                argFormat=$(jq ".lang.${ii##*.}.function.arg.format" ./style.json | tr -d "\"")
                argSep=$(jq ".lang.${ii##*.}.function.arg.sep" ./style.json | tr -d "\"")
                defaultDiv=${argFormat##*"argName"}
                defaultDiv=${defaultDiv:0:1}
                argEnd=$(echo ${argFormat##*"default"} | tr -d '[:space:]')
                argStart=$(echo ${argFormat%%"argName"*}| tr -d '[:space:]')

                topwrite $c $i $(jq ".lang.${ii#*.}.name" ./style.json | tr -d '\"' )          
                while IFS= read -rs line; do
                    lzw=$(echo -e "$line" | tr -d '[:blank:]')
                    param=$(echo $test | tr -d '[:blank:]')
                    if [[ $lzw =~ $param ]]; then
                        A=$(echo $lzw |  sed -r 's/'$param'//g')
                        A=${A#*$argStart}
                        if ! [[ -z $argEnd ]]; then
                            A=${A%*$argEnd}                         
                        fi
                        IFS=${argSep} read -a array <<< "$A"
                        unset IFS       

                        N=$(grep -Fn "$line" $i | cut -d ":" -f1)
                        M=$(($N + 4 + ${#array[@]}))

                        if [[ -z $(sed -n "$N,$M{/$FNTEST/{=;p}}" $i) ]]; then
                            sed -i '/'"$line"'/a '"$c"'> '"$FNTEST" $i
                        fi

                        if [[ -z $(sed -n "$N,$M{/$RETURN/{=;p}}" $i) ]]; then
                            sed -i '/'"$line"'/a '"$c"'> '"$RETURN" $i
                        fi

                        for val in $(echo "${array[@]}" | tac -s ' '); do
                            if [ $(echo "$val" | grep -c $defaultDiv ) -ne 0 ]; then
                                default=$(echo "$val" | cut -d $defaultDiv -f2 | tr -d "\"")
                                val=$(echo "$val" | cut -d $defaultDiv -f1)
                                ARGS="param type \[$default\] $val:"
                            else
                                ARGS="param type $val:"
                            fi
                            if [[ -z $(sed -n "$N,$M{/$ARGS/{=;p}}" $i) ]]; then
                                sed -i '/'"$line"'/a '"$c"'> '"$ARGS" $i
                            fi
                        done
                        
                        if [[ -z $(sed -n "$N,$M{/$DETAIL/{=;p}}" $i) ]]; then
                            sed -i '/'"$line"'/a '"$c"'> '"$DETAIL" $i
                        fi
                    else
                        continue
                    fi
                done  < "$i"       
            fi
        done
    ;; 
    "ref" ) 
        if [ ! -e $ODIR ]; then
            mkdir $ODIR
        fi
        if [ ! -e $ODIR/../docs ]; then
            mkdir $ODIR/../docs
        fi

        if [ ! -e $APIDOC ]; then
            touch $APIDOC
        fi

        if [ ! -e $ODIR/index.rst ]; then
            touch $ODIR/index.rst
            HEADER="Application Documentation"
            echo -e "\n$(repeat "-" ${#HEADER})\n$HEADER\n$(repeat "-" ${#HEADER})" >> $ODIR/index.rst
            echo -e ".. toctree::\n\tapi-reference.rst" >> $ODIR/index.rst
        fi 

        echo -e "$(repeat "*" ${#TITLE})\n$TITLE\n$(repeat "*" ${#TITLE})" > $APIDOC

        for i in ${DIR[@]}; do
            ii=${i##*/}           

            if ! [[ $(jq ".lang.${ii##*.}" ./style.json) == null ]]; then
				echo -e "Test: ${ii} ${ii##*.}"
                echo -e "\n$(repeat "-" ${#ii})\n$ii\n$(repeat "-" ${#ii})" >> $APIDOC
                c=$(jq ".lang.${ii##*.}.comment" ./style.json | tr -d '\"' )
                test=$(jq ".lang.${ii##*.}.function.tag" ./style.json | tr -d '[]\"[:space:]')

                argFormat=$(jq ".lang.${ii##*.}.function.arg.format" ./style.json | tr -d "\"")
                argEnd=$(echo ${argFormat##*"default"} | tr -d '[:space:]')
                argStart=$(echo ${argFormat%%"argName"*}| tr -d '[:space:]')

                while IFS= read -rs line; do
                    lzw=$(echo -e "$line" | tr -d '[:space:]')
                    param=$(echo ${test} | tr -d '[:blank:]')
                    if [[ $lzw =~ ^"$c>".*[a-z].*":".* ]]; then
                        if [[ $(echo $lzw | cut -d ":" -f1) != $(echo "$c>$FNTEST" | tr -d '[:space:]' | cut -d ':' -f1) ]]; then
                            Line=$(echo $line | cut -d '>' -f2- | sed "s/^[ \t]*//")
                            echo -e "\t:${Line}" >> $APIDOC
                        fi
                    elif [[ $lzw =~ $param ]]; then  
                            func=$(echo $lzw)
                            if ! [[ -z $argEnd ]]; then
                                func=${func::-1}
                            fi
                            func=$(echo $func |  sed -re 's/'$param'//g')
                            echo -e "\n.. function:: ${func}\n" >> $APIDOC
                    else
                            continue
                    fi
                done < "$i"
            fi
        done

    ;; 
esac 
