$(function(){

	var $template = $('#table-notes-tmpl'),
		$notebook = $('#select-notebook').val(),
		$modal = UIkit.modal('#modal-loading'),
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
				$modal.show();
				$.ajax({
					url: url,
					success: function(data){
						$fnTemplateHelper('table-notes-tmpl', '#table-notes', data);
					},
					complete: function(xhr, ts){
						$modal.hide();
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
		};

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