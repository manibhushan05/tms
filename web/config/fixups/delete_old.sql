


delete from prod_aaho.team_lrnumber where id <= (select max(id) from freeze_aaho.team_lrnumber);

delete from prod_aaho.team_commissiononlyinvoice where id <= (select max(id) from freeze_aaho.team_commissiononlyinvoice);
delete from prod_aaho.team_ownerreceipt where id <= (select max(id) from freeze_aaho.team_ownerreceipt);
delete from prod_aaho.team_topayinvoice where id <= (select max(id) from freeze_aaho.team_topayinvoice);


delete from prod_aaho.team_tbbinvoice_bookings where id <= (select max(id) from freeze_aaho.team_tbbinvoice_bookings);
delete from prod_aaho.team_tbbinvoice where id <= (select max(id) from freeze_aaho.team_tbbinvoice);

delete from prod_aaho.team_inwardpayment_booking_id where id <= (select max(id) from freeze_aaho.team_inwardpayment_booking_id);

delete from prod_aaho.team_outwardpaymentbill_outward_pmt where id <= (select max(id) from freeze_aaho.team_outwardpaymentbill_outward_pmt);
delete from prod_aaho.team_outwardpayment_booking_id where id <= (select max(id) from freeze_aaho.team_outwardpayment_booking_id);
delete from prod_aaho.team_outwardpaymentbill where id <= (select max(id) from freeze_aaho.team_outwardpaymentbill);


delete from prod_aaho.team_outwardpayment where id not in (1961, 1962, 1968, 2182) and id <= (select max(id) from freeze_aaho.team_outwardpayment);
delete from prod_aaho.team_inwardpayment where id not in (943, 1052, 1056) and id <= (select max(id) from freeze_aaho.team_inwardpayment);

delete from prod_aaho.team_manualbooking where id <= (select max(id) from freeze_aaho.team_manualbooking) and id not in (
    1134,1320,1133,1180,1172,1191,1082,1051,1192,1215,1306,1239,1210,1256,
    1336,1268,1337,1066,1088,1385,1269,1138,1024,1371,1011,1209,1307,1343,
    1104,1363,714,1146,1310,1386,1038,1171,1067,1257,1305,1214,1217,1216,
    1277,1290,1289,1314,1362,1313,1315,1319,1300,1325,1365,1364,1299,1361,
    707,1044,1041,1089,1296,1087
);



delete from prod_up_aaho.team_lrnumber where id > (select max(id) from freeze_aaho.team_lrnumber);

delete from prod_up_aaho.team_commissiononlyinvoice where id > (select max(id) from freeze_aaho.team_commissiononlyinvoice);
delete from prod_up_aaho.team_ownerreceipt where id > (select max(id) from freeze_aaho.team_ownerreceipt);
delete from prod_up_aaho.team_topayinvoice where id > (select max(id) from freeze_aaho.team_topayinvoice);


delete from prod_up_aaho.team_tbbinvoice_bookings where id > (select max(id) from freeze_aaho.team_tbbinvoice_bookings);
delete from prod_up_aaho.team_tbbinvoice where id > (select max(id) from freeze_aaho.team_tbbinvoice);

delete from prod_up_aaho.team_inwardpayment_booking_id where id > (select max(id) from freeze_aaho.team_inwardpayment_booking_id);

delete from prod_up_aaho.team_outwardpaymentbill_outward_pmt where id > (select max(id) from freeze_aaho.team_outwardpaymentbill_outward_pmt);
delete from prod_up_aaho.team_outwardpayment_booking_id where id > (select max(id) from freeze_aaho.team_outwardpayment_booking_id);
delete from prod_up_aaho.team_outwardpaymentbill where id > (select max(id) from freeze_aaho.team_outwardpaymentbill);


delete from prod_up_aaho.team_outwardpayment where id > (select max(id) from freeze_aaho.team_outwardpayment);
delete from prod_up_aaho.team_inwardpayment where  id > (select max(id) from freeze_aaho.team_inwardpayment);

delete from prod_up_aaho.team_manualbooking where id > (select max(id) from freeze_aaho.team_manualbooking);




delete from prod_up_aaho.team_lrnumber where created_on = updated_on or updated_on <= (select max(updated_on) from freeze_aaho.team_lrnumber);

delete from prod_up_aaho.team_commissiononlyinvoice where created_on = updated_on or updated_on <= (select max(updated_on) from freeze_aaho.team_commissiononlyinvoice);
delete from prod_up_aaho.team_ownerreceipt where created_on = updated_on or updated_on <= (select max(updated_on) from freeze_aaho.team_ownerreceipt);
delete from prod_up_aaho.team_topayinvoice where created_on = updated_on or updated_on <= (select max(updated_on) from freeze_aaho.team_topayinvoice);


delete from prod_up_aaho.team_tbbinvoice_bookings where tbbinvoice_id in (
  select id from prod_up_aaho.team_tbbinvoice where created_on = updated_on or updated_on <= (select max(updated_on) from freeze_aaho.team_tbbinvoice)
);
delete from prod_up_aaho.team_tbbinvoice where created_on = updated_on or updated_on <= (select max(updated_on) from freeze_aaho.team_tbbinvoice);

delete from prod_up_aaho.team_inwardpayment_booking_id where inwardpayment_id in (
  select id from prod_up_aaho.team_inwardpayment where created_on = updated_on or updated_on <= (select max(updated_on) from freeze_aaho.team_inwardpayment)
);
delete from prod_up_aaho.team_inwardpayment where created_on = updated_on or updated_on <= (select max(updated_on) from freeze_aaho.team_inwardpayment);


delete from prod_up_aaho.team_outwardpaymentbill_outward_pmt where outwardpaymentbill_id in (
  select id from prod_up_aaho.team_outwardpaymentbill where created_on = updated_on or updated_on <= (select max(updated_on) from freeze_aaho.team_outwardpaymentbill)
);
delete from prod_up_aaho.team_outwardpaymentbill where created_on = updated_on or updated_on <= (select max(updated_on) from freeze_aaho.team_outwardpaymentbill);

delete from prod_up_aaho.team_outwardpayment_booking_id where outwardpayment_id in (
  select id from prod_up_aaho.team_outwardpayment where created_on = updated_on or updated_on <= (select max(updated_on) from freeze_aaho.team_outwardpayment)
);
delete from prod_up_aaho.team_outwardpayment where created_on = updated_on or updated_on <= (select max(updated_on) from freeze_aaho.team_outwardpayment);

delete from prod_up_aaho.team_manualbooking where updated_on <= (select max(updated_on) from freeze_aaho.team_manualbooking) and id not in (1332,1316,1301,1135,1295,1187);




select count(*) from prod_aaho.team_commissiononlyinvoice;
select count(*) from prod_aaho.team_inwardpayment;
select count(*) from prod_aaho.team_inwardpayment_booking_id;
select count(*) from prod_aaho.team_lrnumber;
select count(*) from prod_aaho.team_manualbooking;
select count(*) from prod_aaho.team_outwardpayment;
select count(*) from prod_aaho.team_outwardpayment_booking_id;
select count(*) from prod_aaho.team_outwardpaymentbill;
select count(*) from prod_aaho.team_outwardpaymentbill_outward_pmt;
select count(*) from prod_aaho.team_ownerreceipt;
select count(*) from prod_aaho.team_tbbinvoice;
select count(*) from prod_aaho.team_tbbinvoice_bookings;
select count(*) from prod_aaho.team_topayinvoice;


select count(*) from prod_up_aaho.team_commissiononlyinvoice;
select count(*) from prod_up_aaho.team_inwardpayment;
select count(*) from prod_up_aaho.team_inwardpayment_booking_id;
select count(*) from prod_up_aaho.team_lrnumber;
select count(*) from prod_up_aaho.team_manualbooking;
select count(*) from prod_up_aaho.team_outwardpayment;
select count(*) from prod_up_aaho.team_outwardpayment_booking_id;
select count(*) from prod_up_aaho.team_outwardpaymentbill;
select count(*) from prod_up_aaho.team_outwardpaymentbill_outward_pmt;
select count(*) from prod_up_aaho.team_ownerreceipt;
select count(*) from prod_up_aaho.team_tbbinvoice;
select count(*) from prod_up_aaho.team_tbbinvoice_bookings;
select count(*) from prod_up_aaho.team_topayinvoice;