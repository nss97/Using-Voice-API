<?php
$lang = $_POST['lang'];
$audio = $_POST['audio'];

$file_name='x.base64';

$save_byte=file_put_contents("static-data/".$file_name, $audio);
// $result = shell_exec("python3 sr.py ".$lang);
// $result = json_decode($result);
// $trans = array('results' => $result, 'op' => $result->score[1]);

$handle=fsockopen("127.0.0.1",1234); 
if($handle&&$save_byte){
	fputs($handle,$lang);
	$result=fgets($handle,1024);
	$result = json_decode($result);
	$trans = array('results' => $result, 'op' => $result->score[1]);
	echo json_encode($trans);
}
?>
