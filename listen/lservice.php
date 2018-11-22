<?php

$lang = $_POST['lang'];
$audio = $_POST['audio'];

file_put_contents("x.base64", $audio);
exec("python sr.py ".$lang, $result);

// echo "baidu: ".$result[0];
// echo  "<br />";
// echo "xunfei: ".$result[1];
// echo $lang;

$trans = array('baidu' => $result[0], 'xunfei' =>$result[1],'caozuo' => $result[2]);
echo json_encode($trans);
// echo $result[1]; 
?>