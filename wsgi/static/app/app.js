$(function(){

	var $template = $('#table-notes-tmpl'),
		$notebook = $('#select-notebook').val(),
		//$modal = UIkit.modal('#modal-loading'),
		$loading = UIkit.notify("<i class='uk-icon-spinner uk-icon-spin'></i> Loading...", {timeout: 0}),
		/**
		  * @breif  A simple wrapper for artTemplate template func.
		  * @param  template_selector, the render template selector
		  * @param  parent_selector, the parent elem to append the template content
		  * @param  data, the data object to render in template
		  * @retval None
		  */
		$fnTemplateHelper = function(template_selector, parent_selector, data){
			var html = template(template_selector, {list: data});
			$(parent_selector).html(html);
		},
		/**
		  * @breif  Get notes with specific notebook GUID
		  * @param  Evernote notebook GUID
		  * @retval None
		  */
		$fnGetNote = function(notebook){
			if(notebook){
				var url = "/notebooks/{0}/notes/".replace('{0}', notebook);
				//$modal.show();
				$loading.show();
				$.ajax({
					url: url,
					success: function(data){
						$fnTemplateHelper('table-notes-tmpl', '#table-notes', data);
					},
					complete: function(xhr, ts){
						//$modal.hide();
						$loading.close();
					}
				});
			}
		},
		/**
		  * @breif  Get github repo with user token
		  * @param  None
		  * @retval None
		  */
		$fnGetGitRepo = function(){
			var url = "/github-repo/"
			$.ajax({
				url: url,
				success: function(data){
					$fnTemplateHelper('repo-tmpl', '#select-repo', data);
				},
				complete: function(){
				}
			});
		},
		$fnDateFormat = function(timestamp){
			var a = new Date(timestamp*1000);
			var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
			var year = a.getFullYear();
			var month = months[a.getMonth()];
			var date = a.getDate();
			var hour = a.getHours();
			var min = a.getMinutes();
			var sec = a.getSeconds();
			var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
			return time;
		};

	// Register dateFormat helper
	template.helper('dateFormat', $fnDateFormat);

	/* notebook select widget changed */
	$('#select-notebook').change(function(){
		$fnGetNote($(this).val());
	});	

	/* First load */
	if($notebook){
		$fnGetNote($notebook);
	}

	/* Load the github repo */
	$fnGetGitRepo();
});