def get_lead_manager_profile_pic_upload_path(instance, filename):
    return "LeadManager/{}/{}".format(instance.user.id, filename.split('/')[-1])
