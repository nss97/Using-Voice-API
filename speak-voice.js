function getVoiceByText(voiceText) {
	var source = "<source src=http://tsn.baidu.com/text2audio?tex=" +
		voiceText +
		"&lan=zh&cuid=123333321&" +
		"ctp=1&tok=24.480ab787cd203dd541c0f69cde74f736.2592000.1544082752.282335-14696121     " +
		"type='audio/mp3'>";

	var vedio = "<video controls='controls' autoplay='autoplay' name='media'>" + source + "</video>"

	$(".vedioDiv").empty();
	$(".vedioDiv").html(vedio);

}

function main() {
	$(document).ready(function() {
		$(".voiceTextBtn").click(function() {
			var voiceText = $(".voiceText").val();
			console.log(voiceText);
			getVoiceByText(voiceText);
		})
	})
}