import styles from '@/styles/components/ItemTransactionMobile.module.scss';
import ValueMosaic from './ValueMosaic';
import ValueTimestamp from './ValueTimestamp';
import ValueAccount from './ValueAccount';
import IconTransactionType from './IconTransactionType';
import ValueTransactionHash from './ValueTransactionHash';
import { useTranslation } from 'next-i18next';
import CustomImage from './CustomImage';


const ItemTransactionMobile = ({ data }) => {
    const { hash, signer, recipient, amount, type, timestamp} = data;
	const { t } = useTranslation();
	const typeText = t(`transactionType_${type}`);

	return (
		<div className={styles.itemTransactionMobile}>
			<IconTransactionType value={type} />
			<div className={styles.middle}>
				{/* <div className={styles.end}> */}
				<div className={styles.type}>{typeText}</div>
				<div className={styles.row}>
					<CustomImage className={styles.iconDirection} src="/images/icon-hash.svg" />
					<ValueTransactionHash value={hash} />
				</div>
				{/* </div> */}
				<ValueAccount address={signer} size="sm" />
				<div className={styles.row}>
					<CustomImage className={styles.iconDirection} src="/images/icon-transaction-direction.svg" />
					<ValueAccount address={recipient} size="sm" />
				</div>

				<div className={styles.end}>
					<ValueTimestamp value={timestamp} hasTime/>
					<ValueMosaic isNative amount={amount} />
				</div>
			</div>
		</div>
	);
}


// const ItemTransactionMobile = ({ data }) => {
//     const { hash, signer, recipient, amount, type, timestamp} = data;
// 	const { t } = useTranslation();
// 	const typeText = t(`transactionType_${type}`);

// 	return (
// 		<div className={styles.itemTransactionMobile}>
// 			{/* <IconTransactionType value={type} /> */}
// 			<div className={styles.middle}>
// 				<div className={styles.type}>{typeText}</div>
// 				<div className={styles.row}>
// 					<div className={styles.title}>From:</div>
// 					<ValueAccount address={signer} size="sm" />
// 				</div>
// 				<div className={styles.row}>
// 					<div className={styles.title}>To:</div>
// 					<ValueAccount address={recipient} size="sm" />
// 				</div>
// 				<div className={styles.row}>
// 					<div className={styles.title}>Hash:</div>
// 					<ValueTransactionHash value={hash} />
// 				</div>
// 				<div className={styles.end}>
// 					<ValueTimestamp value={timestamp} hasTime/>
// 					<ValueMosaic isNative amount={amount} />
// 				</div>
// 			</div>
// 		</div>
// 	);
// }

export default ItemTransactionMobile;
