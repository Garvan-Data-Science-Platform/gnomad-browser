import { Factory } from 'fishery'
import { GtexTissueExpression } from '../GenePage/TranscriptsTissueExpression'

export const gtexTissueExpressionFactory = Factory.define<GtexTissueExpression>(({ params }) => {
  const {
    adipose_subcutaneous = 0,
    adipose_visceral_omentum = 0,
    adrenal_gland = 0,
    artery_aorta = 0,
    artery_coronary = 0,
    artery_tibial = 0,
    bladder = 0,
    brain_amygdala = 0,
    brain_anterior_cingulate_cortex_ba24 = 0,
    brain_caudate_basal_ganglia = 0,
    brain_cerebellar_hemisphere = 0,
    brain_cerebellum = 0,
    brain_cortex = 0,
    brain_frontal_cortex_ba9 = 0,
    brain_hippocampus = 0,
    brain_hypothalamus = 0,
    brain_nucleus_accumbens_basal_ganglia = 0,
    brain_putamen_basal_ganglia = 0,
    brain_spinal_cord_cervical_c_1 = 0,
    brain_substantia_nigra = 0,
    breast_mammary_tissue = 0,
    cells_ebv_transformed_lymphocytes = 0,
    cells_transformed_fibroblasts = 0,
    cervix_ectocervix = 0,
    cervix_endocervix = 0,
    colon_sigmoid = 0,
    colon_transverse = 0,
    esophagus_gastroesophageal_junction = 0,
    esophagus_mucosa = 0,
    esophagus_muscularis = 0,
    fallopian_tube = 0,
    heart_atrial_appendage = 0,
    heart_left_ventricle = 0,
    kidney_cortex = 0,
    liver = 0,
    lung = 0,
    minor_salivary_gland = 0,
    muscle_skeletal = 0,
    nerve_tibial = 0,
    ovary = 0,
    pancreas = 0,
    pituitary = 0,
    prostate = 0,
    skin_not_sun_exposed_suprapubic = 0,
    skin_sun_exposed_lower_leg = 0,
    small_intestine_terminal_ileum = 0,
    spleen = 0,
    stomach = 0,
    testis = 0,
    thyroid = 0,
    uterus = 0,
    vagina = 0,
    whole_blood = 0,
  } = params
  return {
    adipose_subcutaneous,
    adipose_visceral_omentum,
    adrenal_gland,
    artery_aorta,
    artery_coronary,
    artery_tibial,
    bladder,
    brain_amygdala,
    brain_anterior_cingulate_cortex_ba24,
    brain_caudate_basal_ganglia,
    brain_cerebellar_hemisphere,
    brain_cerebellum,
    brain_cortex,
    brain_frontal_cortex_ba9,
    brain_hippocampus,
    brain_hypothalamus,
    brain_nucleus_accumbens_basal_ganglia,
    brain_putamen_basal_ganglia,
    brain_spinal_cord_cervical_c_1,
    brain_substantia_nigra,
    breast_mammary_tissue,
    cells_ebv_transformed_lymphocytes,
    cells_transformed_fibroblasts,
    cervix_ectocervix,
    cervix_endocervix,
    colon_sigmoid,
    colon_transverse,
    esophagus_gastroesophageal_junction,
    esophagus_mucosa,
    esophagus_muscularis,
    fallopian_tube,
    heart_atrial_appendage,
    heart_left_ventricle,
    kidney_cortex,
    liver,
    lung,
    minor_salivary_gland,
    muscle_skeletal,
    nerve_tibial,
    ovary,
    pancreas,
    pituitary,
    prostate,
    skin_not_sun_exposed_suprapubic,
    skin_sun_exposed_lower_leg,
    small_intestine_terminal_ileum,
    spleen,
    stomach,
    testis,
    thyroid,
    uterus,
    vagina,
    whole_blood,
  }
})
