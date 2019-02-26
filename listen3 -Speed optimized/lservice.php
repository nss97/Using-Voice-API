<?php


@$lang = $_POST['lang'];
@$audio = $_POST['audio'];

$file_name='x.base64';

file_put_contents("static-data/".$file_name, $audio);
// exec("python sr.py ".$lang, $result);
// 
$handle = fsockopen("127.0.0.1",1234); 
if($handle){
	fputs($handle,$lang);  
    // while($line=fgets($handle,1024)){  
    //     echo $line;  
    // }  
    $trans=fgets($handle,1024);
    // echo $baidu;
    // $xunfei=fgets($handle,1024);
    // echo $xunfei;
    // $caozuo=fgets($handle,1024);
    // echo $caozuo;
    echo $trans;
} 
// $trans = array('baidu' => $baidu, 'xunfei' =>$xunfei,'caozuo' => $caozuo);

?>
