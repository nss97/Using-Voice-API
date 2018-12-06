<?php


$lang = $_POST['lang'];
$audio = $_POST['audio'];

date_default_timezone_set('PRC');
// now time + random: month+day+hour+minute+seconde + _ +
$file_name=date('mdHis',time()).'_'.mt_rand(10,99).'.base64';

file_put_contents("base64/".$file_name, $audio);
exec("python sr.py ".$lang." ".$file_name, $result);

$trans = array('baidu' => $result[0], 'xunfei' =>$result[1],'caozuo' => $result[2]);
echo json_encode($trans);
?>